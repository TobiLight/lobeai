#!/usr/bin/python3
# File: prompt.py
# Author: Oluwatobiloba Light

from fastapi import APIRouter, Depends, HTTPException, status
from schemas.query import QueryPrompt
from schemas.user import UserProfile
from src.utils.aiquery import generate_mongo, generate_sql, \
    get_applicable_tables_sql, query_response_to_nl
from src.utils.auth import custom_auth
from uuid import uuid4
from prisma import errors
from datetime import datetime

prompt_router = APIRouter(
    responses={404: {"description": "Not Found!"}}, tags=["User Prompts"])


@prompt_router.post("/create-prompt", summary="Create a prompt")
async def create_prompt(query: QueryPrompt,
                        user: UserProfile = Depends(custom_auth)):
    """
    Creates a prompt based on the provided query and user profile.

    Args:
        query (QueryPrompt): The query prompt object containing information
        for prompt creation.
        user (UserProfile, optional): The user profile obtained through
        custom authentication. Defaults to None if not provided.

    Returns:
        Natural language
    """
    def add_quotes_around_table(query):
        # Ensure query is a string
        import re
        if not isinstance(query, str):
            raise ValueError("Input must be a string")

        # Define a regular expression pattern to match schema.table
        pattern = r'(\bpublic\b)\.(\w+)'

        # Use re.sub to replace matches
        modified_query = re.sub(
            pattern, lambda match: f'{match.group(1)}."{match.group(2)}"',
            query)
        return modified_query

    data = {}
    if not query:
        return {"status": "Error", "message": "Query cannot be empty!"}
    from src.db import db as prismadb

    # check if database already exists
    existing_db = await prismadb.databaseconnection.\
        find_unique(where={"id": query.database_id})
    if not existing_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database does not exist! Consider adding a new database!",
            headers={"Authorization": "Bearer"})
    existing_convo = await prismadb.conversation.\
        find_unique(where={"id": query.conversation_id})
    if not existing_convo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation does not exist!",
            headers={"Authorization": "Bearer"})

    if existing_db.type in ["postgresql", "mysql"]:
        from sqlalchemy import create_engine, MetaData, text
        from sqlalchemy.orm import sessionmaker

        engine = create_engine(existing_db.uri)
        metadata = MetaData()
        metadata.reflect(bind=engine)
        postgres_session = sessionmaker(bind=engine)()

        table_names = list(metadata.tables.keys())
        get_tables = get_applicable_tables_sql(query.query, table_names)

        if existing_db.type == 'postgresql':
            get_tables_keys = get_tables.replace('"', "").split(", ")
            for table_name, table in metadata.tables.items():
                # Extract column names
                column_names = [column.name for column in table.columns]

                # Store in the dictionary
                data[table_name] = column_names
            sql_command = generate_sql(
                query.query, data, "The schema name for this database is\
                    'public'.", "PostgreSQL")
        else:
            get_tables_keys = get_tables.replace('"', "").split(", ")
            for table_name, table in metadata.tables.items():
                # Extract column names
                column_names = [column.name for column in table.columns]

                # Store in the dictionary
                data[table_name] = column_names
            sql_command = generate_sql(
                query.query, data, "", "MySQL")

        sql_query = text('{}'.format(sql_command))
        modified_query = add_quotes_around_table(str(sql_query))
        print(data)
        print(modified_query, sql_query)

        try:
            sql_result = postgres_session.execute(text(modified_query)).all()
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An error has occured while querying the database!Please try again :)")
        response = query_response_to_nl(query.query, sql_result)

        try:
            user_prompts = await prismadb.prompt.create({
                "id": str(uuid4()),
                "query": query.query,
                "response": response,
                "conversation_id": query.conversation_id,
                # "user_id": user.id
            })
            conversation = await prismadb.conversation.\
                update(where={"id": query.conversation_id},
                       data={"prompts": {"connect":
                                         [{"id": user_prompts.id}]},
                             "updated_at": datetime.now()})
        except errors.PrismaError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="{}".format(e))

        postgres_session.close()
        return {"status": "Ok", "data": response}

    from pymongo import MongoClient, errors as pyerrors
    try:
        mongodb = MongoClient(existing_db.uri)
    except (pyerrors.PyMongoError, ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Database connection failed!")
    db = mongodb["{}".format(existing_db.database_name)]
    list_of_collections = db.list_collection_names()
    get_tables = get_applicable_tables_sql(query.query, list_of_collections)
    get_tables_keys = get_tables.replace('"', "").split(", ")
    for table in get_tables_keys:
        columns = list(db.get_collection(table).find_one().keys())
        data[table] = columns
    mongo_command = generate_mongo(query.query, data)
    try:
        print("mongo command: ", mongo_command)
        mongo_response = eval("{}".format(mongo_command))
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error has occured while querying the database! Please try again :)")
    mongo_nl_response = query_response_to_nl(query.query, mongo_response)
    try:
        mongo_prompts = await prismadb.prompt.create({
            "id": str(uuid4()),
            "query": query.query,
            "response": mongo_nl_response,
            "conversation_id": query.conversation_id
        })
        await prismadb.conversation.update(where={"id": query.conversation_id},
                                           data={"prompts": {"connect":
                                                             [{"id": mongo_prompts.id}]},
                                                 "updated_at": datetime.now()})
    except errors.PrismaError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="{}".format(e))

    return {"status": "Ok", "data": mongo_nl_response}
