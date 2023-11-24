from typing import Union
from pydantic import BaseModel


class TokenPayload(BaseModel):
    # sub: Union[str, None] = None
    exp: int
    # iss: Union[str, None] = None
    user_id: Union[str, None] = None


class TokenResponse(BaseModel):
    """
    Token Response class
    """
    access_token: str
    token_type: str
