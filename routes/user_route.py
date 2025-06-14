from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
import secrets
from auth.auth_service import get_current_user
from auth.authentication import Auth
from models.user import User
from db.database import get_db
from schema.user_schema import UserCreate, UserRead, \
    UserSuccessResponse, UserDeleteResponse
from queries.user_queries import UserQueries
from exceptions.orm import UserNotFound, UserAlreadyExist

user_router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)


@user_router.get("/{username}", response_model=UserSuccessResponse)
async def get_user(username: str, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    user = UserQueries.get_user_by_username(db=db, username=username)
    if not user:
        raise UserNotFound(status_code=status.HTTP_404_NOT_FOUND,
                           detail="User not found")

    return UserSuccessResponse(
        message="User Fetched Successfully",
        payload=UserRead.model_validate(user),
        status=status.HTTP_200_OK
    )


@user_router.post("/create", response_model=UserSuccessResponse,
                  status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = UserQueries.get_user_by_email(db=db,
                                                  email=str(user_data.email))
    if existing_user:
        raise UserAlreadyExist(status_code=status.HTTP_400_BAD_REQUEST,
                               detail="Email already exists")
    hashed_pw = Auth.hash_password(user_data.password)
    secret_key = secrets.token_urlsafe(64)
    new_user = User(
        username=user_data.username,
        email=str(user_data.email),
        password=hashed_pw,
        secret_key=secret_key
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserSuccessResponse(
        message="User Created Successfully",
        payload=UserRead.model_validate(new_user),
        status=status.HTTP_201_CREATED
    )


@user_router.delete("/{username}", status_code=status.HTTP_200_OK,
                    response_model=UserDeleteResponse)
async def delete_user(username: str, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    user = UserQueries.get_user_by_username(db=db, username=username)
    if not user:
        raise UserNotFound(status_code=status.HTTP_404_NOT_FOUND,
                           detail="User not found")
    db.delete(user)
    db.commit()

    return UserDeleteResponse(
        message="User Deleted Successfully",
        status=status.HTTP_200_OK
    )


@user_router.put("/{username}", response_model=UserSuccessResponse)
async def update_user(username: str, user_data: UserCreate,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    user = UserQueries.get_user_by_username(db=db, username=username)
    if not user:
        raise UserNotFound(status_code=status.HTTP_404_NOT_FOUND,
                           detail="User not found")
    user.username = user_data.username
    user.email = str(user_data.email)
    hashed_pw = Auth.hash_password(user_data.password)
    user.password = hashed_pw
    db.commit()
    db.refresh(user)
    return UserSuccessResponse(
        message="User Updated Successfully",
        payload=UserRead.model_validate(user),
        status=status.HTTP_200_OK
    )
