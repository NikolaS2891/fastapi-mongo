from enum import Enum
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    read_only = "read_only"


class UserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    is_active: str
    created_at: Optional[str] = None
    last_login: str
    password: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "username": "john@mail.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "simple mortal",
                "is_active": "false",
                "created_at": "datetime",
                "last_login": "datetime",
                "password": "fakehashedsecret",
            }
        }


class UpdateUserModel(BaseModel):
    username: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    role: Optional[UserRole]
    is_active: Optional[str]
    created_at: Optional[str]
    last_login: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "username": "john@mail.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "simple mortal",
                "is_active": "false",
                "created_at": "datetime",
                "last_login": "datetime",
            }
        }


class ShowUserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    role: Optional[UserRole]
    is_active: Optional[str]
    created_at: Optional[str]
    last_login: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "username": "john@mail.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "simple mortal",
                "created_at": "datetime",
                "last_login": "datetime",
            }
        }
