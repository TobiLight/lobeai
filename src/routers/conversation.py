from fastapi import APIRouter, Depends
from schemas.user import UserProfile
from src.utils.auth import custom_auth
from src.db import db

conversation_router = APIRouter(
    responses={404: {"description": "Not Found!"}}, tags=["Conversation"])


@conversation_router.get("/conversations", summary="Get all conversations")
async def get_conversations(user: UserProfile = Depends(custom_auth)):
    """"""
    conversations = await db.conversation.find_many()
    return {
        "status": "Ok",
        "data": conversations
    }


@conversation_router.get("/conversation", summary="Get a conversation")
async def get_conversation(conversation_id: str):
    """"""
    conversation = await db.conversation.find_unique(where={"id": conversation_id})
    return {
        "status": "Ok",
      		"conversation_id": conversation_id
    }


@conversation_router.get("/create-conversation", summary="Create a conversation")
async def create_conversation():
    """"""
    return {"status": "Ok"}
