from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSuccessResponse(BaseModel):
    message: str
    payload: UserRead
    status: int


class UserErrorResponse(BaseModel):
    error: str
    status: int


class UserDeleteResponse(BaseModel):
    message: str
    status: int
