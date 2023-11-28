#!/usr/bin/python3
# File: auth.py
# Author: Oluwatobiloba Light

from typing import Any, Dict, Union
from fastapi import Depends, HTTPException, Request, status
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from schemas.token import TokenPayload
from schemas.user import UserProfile
from src.db import db
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth import exceptions
from uuid import uuid4
from prisma import errors
from os import getenv


google_request = requests.Request()

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
JWT_REFRESH_SECRET_KEY = "kjhgfghjk"

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using a secure hashing algorithm.

    Args:
        password (str): The plain-text password to be hashed.

    Returns:
        str: The hashed representation of the input password.
    """
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    """
    Verify whether a given plain-text password matches a hashed password.

    Args:
        password (str): The plain-text password to be verified.
        hashed_pass (str): The hashed password for comparison.

    Returns:
        bool: True if the plain-text password matches the hashed password,
        False otherwise.
    """
    return password_context.verify(password, hashed_pass)


def create_access_token(payload: TokenPayload) -> str:
    """
    Create an access token for the specified subject with an optional
    expiration time.

    Args:
        subject (Union[str, Any]): The subject for which the access token is
        created.
        expires_delta (Union[int, None]): Optional. The expiration time for the
        access token in seconds from the current time. If not provided or set
        to None, the token may not expire.

    Returns:
        str: The generated access token as a string.
    """
    if payload.exp is not None:
        expires = datetime.now(
            tz=timezone.utc) + timedelta(minutes=payload.exp)
    else:
        expires = datetime.now(
            tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"user_id": payload.user_id, "exp": expires,
                 #  "sub": str(payload.sub), "iss": payload.iss
                 }
    encoded_jwt = jwt.encode(to_encode, getenv(
        "JWT_SECRET_KEY"), getenv("ALGORITHM"))
    return encoded_jwt


# def create_refresh_token(subject: Union[str, Any], expires_delta: Union[int, None] = None) -> str:
#     if expires_delta is not None:
#         expires_delta = datetime.utcnow() + expires_delta
#     else:
#         expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

#     to_encode = {"exp": expires_delta, "sub": str(subject)}
#     encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
#     return encoded_jwt

def decode_token(token: str) -> Union[str, None]:
    """"""
    try:
        payload = jwt.decode(token, getenv(
            "JWT_SECRET_KEY"), getenv("ALGORITHM"))
        token_data = TokenPayload(**payload)

        # if datetime.fromtimestamp(token_data.exp).timestamp() < datetime.now().timestamp():
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Token expired",
        #         headers={"WWW-Authenticate": "Bearer"},
        #     )
    except (JWTError, ExpiredSignatureError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if token_data.email:
        return token_data.email
    return None


async def decode_google_token(request: Request) -> UserProfile:
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
    return id_info

    if id_info["iss"] == "https://accounts.google.com":
        try:
            existing_user = await db.user.find_unique(where={"email": id_info["email"]})
            print("existing user", existing_user)
            if existing_user:
                return existing_user
            else:
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
                # new_user = {
                #     "id": new_user.id,
                #     "email": new_user.email,
                #     "name": new_user.name
                # }
            return new_user
        except errors.PrismaError as e:
            print(e)
            print("An error has occured!")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Something went wrong!", headers={"Authorization": "Bearer {}".format(token)})

    return None


async def custom_auth(token: Dict[str, Any] = Depends(decode_google_token)) -> UserProfile:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials!", headers={"Authorization": "Bearer"})
    if token['iss'] == 'https://accounts.google.com':
        existing_user = await db.user.find_unique(where={"email": token["email"]})

        if existing_user:
            user = {
                'id': existing_user.id,
                "email": existing_user.email,
                "name": existing_user.name,
                "created_at": existing_user.created_at,
                "updated_at": existing_user.updated_at
            }
            return user
        else:
            return token
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials!", headers={"Authorization": "Bearer"})
