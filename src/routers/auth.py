#!/usr/bin/python3
# File: auth.py
# Author: Oluwatobiloba Light

from datetime import timedelta, datetime
from typing import Any, Dict, Union
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from schemas.token import TokenPayload
from schemas.user import UserProfile, UserSignUp, UserSignupOutput
from src.db import db
from uuid import uuid4
from src.utils.auth import create_access_token, custom_auth, hash_password, verify_password
from os import getenv
from prisma import errors
from jose import jwt
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth import exceptions


auth_router = APIRouter(prefix="/auth", tags=["auth"],
                        responses={404: {"description": "Not Found!"}})

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
google_request = requests.Request()


@auth_router.post("/signup", summary="Create a new user",
                  response_model=Union[UserSignupOutput, dict],
                  response_model_exclude_none=True)
async def create_user(form_data: UserSignUp):
    """
    """
    if len(form_data.password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Password must contain 6 or more characters")
    existing_user = await db.user.find_unique(where={"email": form_data.email})
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="This email is already registered!")

    user = await db.user.create({
        "id": str(uuid4()),
        "email": form_data.email,
        "password": hash_password(form_data.password),
        "first_name": form_data.first_name,
        "last_name": form_data.last_name
    })
    return {
        "message": "Account created successfully",
        "email": user.email
    }


@auth_router.post("/login", summary="User login", response_model=Union[UserProfile, dict], response_model_exclude_none=True)
async def login(request: Request):
    """
    Logs a user in and return access token
    """
    token: str = ""
    if not request.headers.get("Authorization"):
        return None
    if len(request.headers.get("Authorization")) < 2:
        return None
    token = request.headers.get("Authorization")
    token = token.split()[1] if len(token.split()) > 1 else ""

    try:
        id_info = id_token.verify_oauth2_token(
            token, google_request)
    except exceptions.GoogleAuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials!", headers={"Authorization": "Bearer"})

    if id_info["iss"] == "https://accounts.google.com":
        existing_user = await db.user.find_unique(where={"email": id_info["email"]})
        if not existing_user:
            try:
                new_user = await db.user.create({
                    "id": str(uuid4()),
                    "email": id_info["email"],
                    "name": id_info["name"],
                }, include={"database_connections": True, "conversations": True})
                default_db = await db.databaseconnection.create({
                    "id": str(uuid4()),
                    "type": "postgresql",
                    "uri": getenv("DEFAULT_DATABASE"),
                    "user_id": new_user.id,
                    "database_name": "railway"
                })
                default_conversation = await db.conversation.create({
                    "id": str(uuid4()),
                    "user_id": new_user.id,
                }, include={"prompts": True})
                default_prompt = await db.prompt.create({
                    "id": str(uuid4()),
                    "query": "How many iPhone X are in stock?",
                    "response": "There are 34 iPhone X in stock.",
                    "conversation_id": default_conversation.id
                })
                update_conversation = await db.conversation.update(where={"id": default_conversation.id},
                                                                   data={"prompts": {"connect": [{"id": default_prompt.id}]}}, include={"prompts": True})
                expiration_time = timedelta(hours=1)
                expiration = datetime.utcnow() + expiration_time
                access_token = jwt.encode(
                    {"user": new_user.email, "exp": expiration}, getenv("JWT_SECRET_KEY"), getenv("ALGORITHM"))
                return {"data": new_user, "access_token": access_token}
            except errors.PrismaError as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="An error has occured", headers={'Authorization': 'Bearer'})
        else:
            expiration_time = timedelta(hours=1)
            expiration = datetime.utcnow() + expiration_time
            access_token = jwt.encode(
                {"user": existing_user.email, "exp": expiration}, getenv("JWT_SECRET_KEY"), getenv("ALGORITHM"))
            return {"data": existing_user, "access_token": access_token}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, headers={
                            "Authorization": "Bearer"}, detail="Invalid credentials!")
