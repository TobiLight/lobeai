#!/usr/bin/python3
# File: auth.py
# Author: Oluwatobiloba Light

from typing import Union
from fastapi import Depends, HTTPException, Request, status
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from schemas.token import TokenPayload
from schemas.user import UserProfile
from src.db import db
from google.auth.transport import requests
from os import getenv
from jose import jwt


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


async def decode_jwt_token(request: Request) -> UserProfile:
    token: str = ""
    if not request.headers.get("Authorization"):
        return None
    if len(request.headers.get("Authorization")) < 2:
        return None
    token = request.headers.get("Authorization")
    token = token.split()[1] if len(token.split()) > 1 else ""
    print("token", token)
    try:
        decoded_token = jwt.decode(token, getenv(
            "JWT_SECRET_KEY"), getenv("ALGORITHM"))
    except (JWTError, ExpiredSignatureError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials!",
                            headers={"Authorization": "Bearer"})

    existing_user = await db.user.find_unique(where={"email":
                                                     decoded_token['user']})
    return existing_user


async def custom_auth(user: UserProfile =
                      Depends(decode_jwt_token)) -> UserProfile:
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="No user found!",
                            headers={"Authorization": "Bearer"})
    data = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }
    return data
