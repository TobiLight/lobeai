import os
from fastapi import APIRouter, Depends, Header, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer
from pydantic import Field
import requests
from jose import jwt
from google.auth import credentials, compute_engine, default
from google.oauth2 import id_token
from google.auth.transport import requests


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./e-commerce-ai-405922-258834ec77fc.json"

google_router = APIRouter(tags=["google auth"])
# oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="/protected", tokenUrl="/auth/google")

# Replace these with your own values from the Google Developer Console
GOOGLE_CLIENT_ID = "22048458494-n54uckb7hjgsuaq2flgi6ort9ggkpo20.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_REDIRECT_URI = "http://localhost:8000/auth/google"


@google_router.get("/login/google")
async def login_google():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"
    }


@google_router.get("/auth/google")
async def auth_google(code: str):
    token_url = "https://accounts.google.com/o/oauth2/token"
    print("code: {}".format(code))
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    # response = requests.post(token_url, data=data)
    # access_token = response.json().get("access_token")
    # print(access_token)
    # user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo",
    #                          headers={"Authorization": f"Bearer {access_token}"})
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo",
                             headers={"Authorization": f"Bearer {access_token}"})
    print("access_token is ", access_token)
    return {**user_info.json(), "access_token": access_token}

@google_router.get("/protected")
async def protected_endpoint(token: str):
    print(token)
    # credentials, project = default()
    idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
    print(idinfo)
    # Extract the token directly from the request parameters
    # decoded_token = jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=["HS256"])
    # print("decoded token", decoded_token)
    # # You can now use the information from the decoded token
    # user_id = decoded_token.get("sub")
    return {"message": "This is a protected endpoint", "user_id": "user_id"}
