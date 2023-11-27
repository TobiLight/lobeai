#!/usr/bin/python3
# File: prompt.py
# Author: Oluwatobiloba Light

from fastapi import APIRouter, Depends
from schemas.query import QueryPrompt
from schemas.user import UserProfile
from src.utils.aiquery import generate_mongo, generate_sql, get_applicable_tables_sql, query_response_to_nl
from src.utils.auth import custom_auth
from uuid import uuid4

prompt_router = APIRouter(
    responses={404: {"description": "Not Found!"}}, tags=["User Prompts"])


@prompt_router.post("/create-prompt", summary="Create a prompt")
async def create_prompt(query: QueryPrompt, user: UserProfile = Depends(custom_auth)):
    """"""
    data = {}
    if not query:
        return {"status": "Error", "message": "Query cannot be empty!"}
    print(query.database_id)
    from src.db import db as prismadb


    # check if database already exists
    existing_db = await prismadb.databaseconnection.find_first(where={"id": query.database_id, "user_id": user.id})
    if not existing_db:
        return {"status": "Error", "message": "Database does not exist! Consider creating a new database!"}

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
            print(data)
            sql_command = generate_sql(
                query.query, get_tables_keys, "The schema name is 'public'.", "PostgreSQL")
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
        # if sql_query in "As "
        try:
            sql_result = postgres_session.execute(sql_query).all()
        except:
            return "An error has occured!"
        response = query_response_to_nl(query.query, sql_result)

        user_prompts = await prismadb.prompt.create({
            "id": str(uuid4()),
            "query": query.query,
            "response": response,
            "conversation_id": query.conversation_id,
        })
        # store prompt in conversation table
        conversation = await prismadb.conversation.update(where={"id": query.conversation_id}, data={"prompts": {"connect": [{"id": user_prompts.id}]}})
        postgres_session.close()
        return {"status": "Ok", "data": response}

    from pymongo import MongoClient

    mongodb = MongoClient(
        "mongodb+srv://0xTobi:ggHrioYrsyJaX7yZ@cluster0.ogakrxv.mongodb.net/")
    db = mongodb["sample_mflix"]
    list_of_collections = db.list_collection_names()
    get_tables = get_applicable_tables_sql(query.query, list_of_collections)
    get_tables_keys = get_tables.replace('"', "").split(", ")
    for table in get_tables_keys:
        columns = list(db.get_collection(table).find_one().keys())
        data[table] = columns
    mongo_command = generate_mongo(query.query, data)
    print("mongo", mongo_command)
    try:
        exec_mongo_command = eval("{}".format(mongo_command))
        print(exec_mongo_command)
    except:
        return "An error has occured"
    print(exec_mongo_command)

    # tables = await client.query_raw('SELECT table_name FROM\
    #     information_schema.tables WHERE table_schema = \'public\';')
    # print(tables)

    return {"status": "Ok"}
