from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from auth.authentication import Auth
from auth.dependencies import get_current_user
from db.redis import get_cached_user, cache_user_data
from middleware.throttling import limiter
from models.user import User
from db.database import get_db
from schema.user_schema import UserCreate, UserRead, \
    UserSuccessResponse, UserDeleteResponse
from queries.user_queries import UserQueries
from exceptions.orm import UserNotFound, UserAlreadyExist

user_router = APIRouter(
    tags=["users"],
)


@user_router.get("/me", response_model=UserSuccessResponse)
async def get_user(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    cached = await get_cached_user(current_user.username)
    if cached:
        return UserSuccessResponse(
            message="User Fetched from Cache",
            payload=UserRead(**cached),
            status_code=status.HTTP_200_OK
        )
    user = UserQueries.get_user_by_username(db=db,
                                            username=current_user.username)
    if not user:
        raise UserNotFound(status_code=status.HTTP_404_NOT_FOUND)

    return UserSuccessResponse(
        message="User Fetched Successfully",
        payload=UserRead.model_validate(user),
        status_code=status.HTTP_200_OK
    )


@user_router.delete("/me", status_code=status.HTTP_200_OK,
                    response_model=UserDeleteResponse)
async def delete_user(db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    user = UserQueries.get_user_by_username(db=db,
                                            username=current_user.username)
    if not user:
        raise UserNotFound(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(user)
    db.commit()

    return UserDeleteResponse(
        message="User Deleted Successfully",
        status=status.HTTP_200_OK
    )


@user_router.patch("/me", response_model=UserSuccessResponse)
async def update_user(user_data: UserCreate,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    user = UserQueries.get_user_by_username(db=db,
                                            username=current_user.username)
    if not user:
        raise UserNotFound(status_code=status.HTTP_404_NOT_FOUND)
    user_by_email = UserQueries.get_user_by_email(db=db, email=user_data.email)
    if user_by_email and user_by_email.email != current_user.email:
        raise UserAlreadyExist(
            detail="Email already exists",
            status_code=status.HTTP_409_CONFLICT
        )
    user_by_username = UserQueries.get_user_by_username(db=db,
                                                        username=user_data.username)
    if user_by_username and user_by_username.username != current_user.username:
        raise UserAlreadyExist(
            detail="Username already exists",
            status_code=status.HTTP_409_CONFLICT
        )
    user.username = user_data.username
    user.email = str(user_data.email)
    hashed_pw = Auth.hash_password(user_data.password)
    user.password_hash = hashed_pw
    db.commit()
    db.refresh(user)
    # Update cache
    await cache_user_data(user.username,
                          UserRead.model_validate(user).model_dump())
    return UserSuccessResponse(
        message="User Updated Successfully",
        payload=UserRead.model_validate(user),
        status_code=status.HTTP_200_OK
    )
