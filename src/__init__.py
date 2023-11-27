from fastapi import APIRouter
from src.routers.auth import auth_router as AuthRouter
from src.routers.index import index_router as IndexRouter
from src.routers.conversation import conversation_router as ConversationRouter
from src.routers.prompt import prompt_router as PromptRouter
# from src.routers.product import seed_data_router as SeedRouter

api = APIRouter()
api.include_router(AuthRouter)
api.include_router(IndexRouter)
api.include_router(ConversationRouter)
api.include_router(PromptRouter)
# api.include_router(SeedRouter)
__all__ = ["api"]
