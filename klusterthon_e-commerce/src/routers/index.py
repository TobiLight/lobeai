#!/usr/bin/python3
# File: index.py

from typing import Union
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, Request, responses
from fastapi import status, responses
from schemas.user import UserProfile
from src.dependencies import get_current_user
from src.utils.aiquery import get_applicable_tables, generate_sql, keys_in_tables, query_response_to_nl
from schemas.query import DatabaseConnection, QueryDB, QueryResponse
from src.db import db as client
from src.utils.auth import decode_token

index_router = APIRouter(responses={404: {"description": "Not Found!"}})


@index_router.get("/", summary="Homepage")
def home():
    return responses.JSONResponse(status_code=status.HTTP_200_OK,
                                  content="Welcome to AI powered E-commerce")


@index_router.post('/query', summary="Query Database with NL")
async def query_database(q: QueryDB, db: DatabaseConnection,
                         current_user: Annotated[QueryResponse,
                                                 Depends(get_current_user)]):
    from prisma import Prisma, Client
    # get connection string from user
    db_conn = await Prisma(datasource={"url":"postgresql://postgres:admin123.@localhost:5433/alx_overflow"}).connect()
    print(db_conn)
    return {}
    # create an instance with the provided string
    # do whatever the fuck we want with the user's database... just kidding.. run queries on it
    # tables = await client.query_raw('SELECT table_name FROM\
    #     information_schema.tables WHERE table_schema = \'public\';')
    # get_tables = get_applicable_tables(q.query, tables)
    # get_tables_keys = await keys_in_tables(get_tables)
    # sql_command = generate_sql(q.query, get_tables_keys)

    # # Response from openai might have await in the command.
    # if 'await' in sql_command:
    #     sql_command = sql_command.replace("await", "").strip()

    # if "." not in sql_command:
    #     return responses.JSONResponse(content={"query": q.query,
    #                                            "response": sql_command})

    # sql_result = await eval("{}".format(sql_command))
    # response = query_response_to_nl(q.query, sql_result)
    # return responses.JSONResponse(content={"query": q.query,
    #                                        "response": response})


# @index_router.post("/get-connection-string", summary="Get DB connection string from a User")
# async def get_connection_string(connection_str: str):
#     """"""
#     # get connection string from user and save it in the database
        
#     return {}