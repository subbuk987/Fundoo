from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from exceptions.auth import InvalidToken, RefreshTokenRequired, \
    AccessTokenRequired
from auth.services import decode_token
from queries.user_queries import UserQueries
from db.redis import token_in_blocklist


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self,
                       request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = decode_token(token)

        if token_data is None:
            raise InvalidToken(
                message="Invalid token. Please login again."
            )

        if await token_in_blocklist(token_data["jti"]):
            raise InvalidToken(
                message="Token is invalid. Please login again."
            )

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data):
        raise NotImplementedError(
            "Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired(
                message="Access Token required."
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired(
                message="Refresh Token required."
            )


async def get_current_user(
        token_details: dict = Depends(AccessTokenBearer()),
        db: Session = Depends(get_db),
):
    username = token_details["user"]["username"]

    user = UserQueries.get_user_by_username(db, username)

    return user
