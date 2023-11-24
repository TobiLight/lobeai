from fastapi import APIRouter
from src.routers.auth import auth_router as AuthRouter
from src.routers.index import index_router as IndexRouter
from src.routers.googleauth import google_router as GoogleRouter

api = APIRouter()
api.include_router(AuthRouter)
api.include_router(IndexRouter)
api.include_router(GoogleRouter)
__all__ = ["api"]
