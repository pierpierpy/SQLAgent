# https://testdriven.io/blog/fastapi-jwt-auth/
from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    fullname: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "fullname": "test",
                "email": "test",
                "password": "test",
            }
        }


class UserLoginSchema(BaseModel):
    email: str = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {"example": {"email": "test", "password": "test"}}
