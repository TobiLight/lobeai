from typing import Union
from pydantic import BaseModel


class TokenPayload(BaseModel):
    name: str
    email: str


class TokenResponse(BaseModel):
    """
    Token Response class
    """
    access_token: str
    token_type: str
