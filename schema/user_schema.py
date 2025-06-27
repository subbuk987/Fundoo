from pydantic import BaseModel, EmailStr, ConfigDict, Field, UUID4
from datetime import datetime



class UserCreate(BaseModel):
    first_name: str = Field(..., pattern=r'^[A-Z][a-zA-Z]{2,}$')
    last_name: str = Field(..., pattern=r'^[A-Z][a-zA-Z]{2,}$')
    username: str
    email: str
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "johndoe@gmail.com",
                "password": "testpass@123"
            }
        }
    }


class UserRead(BaseModel):
    id: UUID4
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSuccessResponse(BaseModel):
    message: str
    payload: UserRead
    status_code: int


class UserErrorResponse(BaseModel):
    error: str
    status: int


class UserDeleteResponse(BaseModel):
    message: str
    status: int


class UserLoginModel(BaseModel):
    username: str
    password: str