#!/usr/bin/python3
# File: user.py
# Author: Oluwatobiloba Light

from typing import Any, Dict, Union
from pydantic import BaseModel


class TokenPayload(BaseModel):
    name: str
    email: str


class TokenResponse(BaseModel):
    """
    Token Response class
    """
    user: Dict[str, Any]


class TokenRequest(BaseModel):
    token: Union[str, None] = None
