#!/usr/bin/python3
# File: conversation.py
# Author: Oluwatobiloba Light

from fastapi import APIRouter, Depends
from schemas.user import UserProfile
from src.utils.auth import custom_auth
from src.db import db
from uuid import uuid4

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
async def get_conversation(conversation_id: str, user: UserProfile = Depends(custom_auth)):
    """"""
    conversation = await db.conversation.find_unique(where={"id": conversation_id})
    return {
        "status": "Ok",
        "conversation_id": conversation
    }


@conversation_router.post("/create-conversation", summary="Create a conversation",)
async def create_conversation(user: UserProfile = Depends(custom_auth)):
    """"""
    new_conversation = await db.conversation.create(data={
        "id": str(uuid4()),
        "user_id": user.id,
        # "prompts": {'connect': list()},
        # "user": {'connect': {"id": user.id}}
        # "prompts": [{"id": "1", "query": "fghj", "response": "sdfg", "user_id": user.id}],
        # "user": user.model_dump_json()
    })

    return {"status": "Ok", "data": new_conversation}