from fastapi import APIRouter
from src.routers.auth import auth_router as AuthRouter
from src.routers.index import index_router as IndexRouter

api = APIRouter()
api.include_router(AuthRouter)
api.include_router(IndexRouter)
__all__ = ["api"]
