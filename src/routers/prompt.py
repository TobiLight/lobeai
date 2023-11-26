#!/usr/bin/python3
# File: prompt.py
# Author: Oluwatobiloba Light

from fastapi import APIRouter, Depends
from schemas.query import QueryPrompt
from schemas.user import UserProfile
from src.utils.aiquery import generate_sql, get_applicable_tables, keys_in_sql_tables, query_response_to_nl
from src.db import db
from src.utils.auth import custom_auth
from uuid import uuid4

prompt_router = APIRouter(
    responses={404: {"description": "Not Found!"}}, tags=["User Prompts"])


@prompt_router.post("/create-prompt", summary="Create a prompt")
async def create_prompt(query: QueryPrompt, user: UserProfile = Depends(custom_auth)):
    """"""
    if not query:
        return {"status": "Error", "message": "Query cannot be empty!"}
    print(query.database_id)

    # check if database already exists
    existing_db = await db.databaseconnection.find_unique(where={"id": query.database_id})
    if not existing_db:
        return {"status": "Error", "message": "Database does not exist! Consider creating a new database"}

    if existing_db.type == 'postgresql':
        from sqlalchemy import create_engine, MetaData, text
        from sqlalchemy.orm import sessionmaker

        engine = create_engine(existing_db.uri)
        metadata = MetaData()
        metadata.reflect(bind=engine)

        table_names = list(metadata.tables.keys())
        get_tables = get_applicable_tables(query, table_names)
        get_tables_keys = await keys_in_sql_tables(get_tables)
        sql_command = generate_sql(query.query, get_tables_keys)
        postgres_session = sessionmaker(bind=engine)()
        sqlcmd = text('{}'.format(sql_command))
        sql_result = postgres_session.execute(sqlcmd).all()
        response = query_response_to_nl(query.query, sql_result)
        # store the prompt
        user_prompts = await db.prompt.create({
            "id": str(uuid4()),
            "query": query.query,
            "response": response,
            "conversation_id": query.conversation_id,
        })
        # store prompt in conversation table
        # conversation = await db.conversation.update(where={"id": query.conversation_id}, data={"prompts": {"connect": [{"id": user_prompts.id}]}})
        # conversation = await db.conversation.update(where={"id": query.conversation_id}, data={"prompts": {"connect": [{"id": user_prompts.id}]}})

        print(conversation)
        return {"status": "Ok", "data": response}

    return {"status": "Ok"}
