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
    conversations = await db.conversation.find_many(where={"user_id": user["id"]}, include={"prompts": {"order_by": {"updated_at": "desc"}}}, order=[{"updated_at": "asc"}])
    return {
        "status": "Ok",
        "data": conversations
    }


@conversation_router.get("/conversation", summary="Get a conversation")
async def get_conversation(id: str, user: UserProfile = Depends(custom_auth)):
    """"""
    conversation = await db.conversation.find_first(where={"id": id, "user_id": user["id"]}, include={"prompts": True}, order=[{"updated_at": "desc"}])
    return {
        "status": "Ok",
        "data": conversation
    }


@conversation_router.post("/create-conversation", summary="Create a conversation",)
async def create_conversation(user: UserProfile = Depends(custom_auth)):
    """"""
    new_conversation = await db.conversation.create({
        "id": str(uuid4()),
        "user_id": user["id"]
    }, include={"prompts": True})

    return {"status": "Ok", "data": new_conversation}
