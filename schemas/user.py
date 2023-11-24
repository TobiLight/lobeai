from typing import Union
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field
import datetime
from prisma.bases import BaseUser

class UserSignUp(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    
class UserSignupOutput(BaseModel):
    message: str
    email: EmailStr
    
class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    
class UserProfile(BaseModel):
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    email: EmailStr
    created_at: datetime.datetime
    
class UserLoginOuput(BaseModel):
    access_token: str
    user: Union[UserProfile, None] = None
    

class UserDetails(BaseUser):
    # id: str
    email: EmailStr
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    def to_json(self):
        """
        Convert User model to JSON
        """
        user_dict = jsonable_encoder(self)
        return user_dict


class UserProfile(BaseModel):
    id: UUID = Field(...)
    email: EmailStr = Field(...)
    first_name: Union[str, None] = Field(default=None)
    last_name: Union[str, None] = Field(default=None)
    created_at: datetime.datetime = Field(default=datetime.datetime.now())
    updated_at: datetime.datetime = Field(default=datetime.datetime.now())
