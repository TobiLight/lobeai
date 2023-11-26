#!/usr/bin/python3
# File: deps.py
# Author: Oluwatobiloba Light
"""Custom dependency for authorization"""

from fastapi import Depends, HTTPException, status
from src.utils.auth import decode_token
from schemas.user import UserProfile
from src.routers.auth import oauth2_scheme
from src.db import db


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserProfile:
    """
    Get the current user based on the provided OAuth2 access token.

    Args:
        token (str): The OAuth2 access token used for user authentication.

    Returns:
        User: An instance of the User model representing the authenticated user.

    Raises:
        HTTPException: If the provided token is invalid or if the user
        cannot be authenticated.
    """
    user_email = decode_token(token)
    user = await db.user.find_unique(where={"email": user_email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserProfile(id=user.id, email=user.email,
                       first_name=user.first_name, last_name=user.last_name,
                       created_at=user.created_at, updated_at=user.updated_at)
