from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from auth.auth_service import authenticate_user, create_access_token
from config.config_loader import settings
from db.database import get_db
from exceptions.auth import AuthError
from schema.token import Token

auth_router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)


@auth_router.post("/login", response_model=Token,
                  status_code=status.HTTP_200_OK)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise AuthError("Invalid credentials")
    access_token_expiry = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    access_token = create_access_token(data={
        "sub": form_data.username
    }, expiry=access_token_expiry)
    return Token(access_token=access_token, token_type="bearer")
