from typing import Union
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from schemas.token import TokenPayload
from schemas.user import UserProfile, UserSignUp, UserSignupOutput
from src.db import db
from uuid import uuid4
from src.utils.auth import create_access_token, hash_password, verify_password


auth_router = APIRouter(prefix="/auth", tags=["auth"],
                        responses={404: {"description": "Not Found!"}})

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


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
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Logs a user in and return access token
    """
    existing_user = await db.user.find_unique(where={"email": form_data.username})
    if existing_user:
        password = verify_password(form_data.password, existing_user.password)
        if password is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, headers={'WWW-Authenticate': 'Bearer'}, detail="Invalid login!")

        payload = TokenPayload(user_id=existing_user.id, exp=30)
        user_token = create_access_token(payload=payload)

        return {"token_type": "bearer", "access_token": user_token}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login!")
