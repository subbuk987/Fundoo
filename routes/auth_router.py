from datetime import timedelta, datetime

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse
from fastapi import Request
from auth.dependencies import RefreshTokenBearer, AccessTokenBearer
from auth.services import create_access_token
from celery_logic.celery_tasks import decode_url_safe_token, \
    send_verification_email_task
from config.config_loader import api_settings
from db.database import get_db
from db.redis import add_jti_to_blocklist, cache_user_data, cache_user_notes, \
    cache_user_labels, clear_user_cache
from exceptions.auth import AuthError, InvalidToken
from exceptions.orm import UserAlreadyExist, UserNotFound
from middleware.throttling import limiter
from queries.note_queries import NoteQueries
from schema.note_schema import NoteRead, LabelRead
from schema.token import Token
from schema.user_schema import UserCreate, UserSuccessResponse, UserRead, \
    UserLoginModel
from queries.user_queries import UserQueries
from auth.authentication import Auth

auth_router = APIRouter(
    tags=["auth"],
)


@auth_router.post("/signup")
@limiter.limit("5/minute")
async def signup(request: Request,user_data: UserCreate, db: Session = Depends(get_db)):
    user_by_username = UserQueries.get_user_by_username(db, user_data.username)
    user_by_email = UserQueries.get_user_by_email(db, user_data.email)

    if user_by_username:
        raise UserAlreadyExist(
            detail="Username already exists",
            status_code=status.HTTP_409_CONFLICT
        )

    if user_by_email:
        raise UserAlreadyExist(
            detail="Email already exists",
            status_code=status.HTTP_409_CONFLICT
        )

    new_user = UserQueries.create_user(db, user_data)

    send_verification_email_task.delay(new_user.username, new_user.email)

    return UserSuccessResponse(
        message="User created",
        payload=UserRead.model_validate(new_user),
        status_code=status.HTTP_201_CREATED
    )


@auth_router.post("/login", response_model=Token,
                  status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login(request: Request, credentials: UserLoginModel, db: Session = Depends(get_db)):
    username = credentials.username
    password = credentials.password

    user = UserQueries.get_user_by_username(db, username)

    if user is None:
        raise AuthError(
            message="Invalid username.",
        )
    data = {
        "username": user.username,
        "user_id": str(user.id)
    }

    if Auth.check_password(password, user.password_hash):
        if not user.is_verified:
            raise AuthError(
                message="User Not Verified. Please verify your email.",
            )
        access_token = create_access_token(data=data,
                                           secret_key=user.secret_key)

        refresh_token = create_access_token(
            data=data,
            secret_key=user.secret_key,
            refresh=True,
            expiry=timedelta(minutes=api_settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        )

        # Cache user, notes, and labels
        await cache_user_data(user.username,
                              UserRead.model_validate(user).model_dump())
        notes = NoteQueries.get_user_notes(db, user)
        await cache_user_notes(user.username,
                               [NoteRead.model_validate(n).model_dump() for n
                                in notes])
        labels = NoteQueries.get_all_labels(
            db)
        await cache_user_labels(user.username,
                                [LabelRead.model_validate(l).model_dump() for l
                                 in labels])
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    raise AuthError(
        message="Invalid Password. Please try again.",
    )


@auth_router.get("/refresh_token")
@limiter.limit("5/minute")
async def get_new_access_token(
        request: Request,
        token_data: dict = Depends(RefreshTokenBearer()),
        db: Session = Depends(get_db)):
    expiry = token_data["exp"]
    username = token_data["user"]["username"]

    user = UserQueries.get_user_by_username(db, username)

    if datetime.fromtimestamp(expiry) > datetime.now():
        new_access_token = create_access_token(
            data=token_data["user"],
            secret_key= str(user.secret_key)
        )

        return JSONResponse({"access_token": new_access_token})

    raise InvalidToken(
        message="Refresh Token Expired. Please Login again.",
    )


@auth_router.get("/logout")
@limiter.limit("5/minute")
async def logout(request: Request, token_data: dict = Depends(AccessTokenBearer())):
    jti = token_data.get("jti")
    username = token_data["user"]["username"]

    await add_jti_to_blocklist(jti)
    await clear_user_cache(username)

    return JSONResponse({
        "message" : "You are now logged out."
    })

@auth_router.get("/verify/{token}")
@limiter.limit("5/minute")
async def verify_user_account(request: Request, token: str, db: Session = Depends(get_db)):

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = UserQueries.get_user_by_email(db, user_email)

        if not user:
            raise UserNotFound(
                detail="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        UserQueries.update_verified_user(user, db)

        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
