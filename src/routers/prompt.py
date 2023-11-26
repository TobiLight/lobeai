#!/usr/bin/python3
# File: prompt.py
# Author: Oluwatobiloba Light

from fastapi import APIRouter
from schemas.query import QueryPrompt
from src.utils.aiquery import get_applicable_tables, keys_in_tables
from src.db import db

prompt_router = APIRouter(
    responses={404: {"description": "Not Found!"}}, tags=["User Prompts"])


@prompt_router.post("/create-prompt", summary="Create a prompt")
async def create_prompt(query: QueryPrompt):
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
        from sqlalchemy.ext.declarative import declarative_base
        import sys

        engine = create_engine(existing_db.uri)
        metadata = MetaData()
        metadata.reflect(bind=engine)

        table_names = list(metadata.tables.keys())
        postgres_session = sessionmaker(bind=engine)()
        get_tables = get_applicable_tables(query, table_names)
        print(get_tables)
        get_tables_keys = await keys_in_tables(get_tables)

    return {"status": "Ok"}
