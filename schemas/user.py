#!/usr/bin/python3
# File: user.py
# Author: Oluwatobiloba Light

from typing import Union
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
import datetime


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
    id: UUID = Field(...)
    email: EmailStr = Field(...)
    # first_name: Union[str, None] = Field(default=None)
    name: Union[str, None] = Field(default=None)
    created_at: datetime.datetime = Field(default=datetime.datetime.now())
    updated_at: datetime.datetime = Field(default=datetime.datetime.now())


class UserLoginOuput(BaseModel):
    access_token: str
    user: Union[UserProfile, None] = None


class UserRequest(BaseModel):
    email: str
    name: str
    profile_photo: Union[str, None] = None
