#!/usr/bin/python3
# File: index.py

from sqlite3 import OperationalError
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, responses, Response
from fastapi import status, responses
from schemas.token import TokenRequest
from schemas.user import UserProfile
from src.dependencies import get_current_user
from schemas.query import DatabaseConnection, QueryDB, QueryResponse
from src.utils.auth import custom_auth, decode_google_token, decode_token
from urllib.parse import urlparse
from google.oauth2 import id_token
from google.auth.transport import requests
from src.db import db
from uuid import uuid4
from prisma import errors

google_request = requests.Request()


index_router = APIRouter(responses={404: {"description": "Not Found!"}})


@index_router.get("/", summary="Homepage")
def home():
    return responses.JSONResponse(status_code=status.HTTP_200_OK,
                                  content="Welcome to AI powered E-commerce")


@index_router.post("/authenticate")
def protected_endpoint(user: Annotated[UserProfile, Depends(custom_auth)]):
    return {"message": "This is a protected endpoint", "user": user}


@index_router.post("/create-db", summary="Create a Database connection from user")
async def create_dbconn(db_conn: DatabaseConnection, request: Request, user: UserProfile = Depends(custom_auth)):
    """"""
    from sqlalchemy import create_engine

    token = request.headers.get("Authorization").split()[1]

    try:
        user = await decode_google_token(token)
    except Exception as e:
        return responses.JSONResponse({"details": "{}".format(e)}, status_code=status.HTTP_400_BAD_REQUEST)

    parsed_url = urlparse(db_conn.uri)

    if not parsed_url.hostname or not parsed_url.path[1:] or parsed_url.path[1:] == '':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid Database URI")

    if db_conn.database_type == 'postgresql':
        engine = create_engine(
            "postgresql+psycopg2://{}:{}@{}:{}/{}".format(parsed_url.username, parsed_url.password, parsed_url.hostname,
                                                          parsed_url.port, parsed_url.path[1:]))
    elif db_conn.database_type == 'mysql':
        engine = create_engine(
            "mysql+mysqldb://{}:{}@{}:{}/{}".format(parsed_url.username, parsed_url.password, parsed_url.hostname,
                                                    parsed_url.port, parsed_url.path[1:]), echo=True)
    else:
        # handle mongodb connection here
        pass

    try:
        engine.connect().close()
        print("Database is connected.")
        existing_conn = await db.databaseconnection.find_first(where={"uri": db_conn.uri})
        if existing_conn:
            return {"status": "Database connection exists already!"}
        await db.databaseconnection.create({
            "id": str(uuid4()),
            "user_id": user.id,
            "uri": db_conn.uri,
            "port": str(parsed_url.port),
            "host": parsed_url.path[1:],
            "username": parsed_url.username,
            "password": parsed_url.password,
            "type": db_conn.database_type
        })
    except (errors.PrismaError, OperationalError) as e:
        print(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="{}".format(e))

    return {"status": "OK"}


@index_router.get("/get-db", summary="Get Database Connection URI")
async def get_dbconn(request: Request):
    """"""
    token = request.headers.get("Authorization").split()[1]

    try:
        user = await decode_google_token(token)
    except Exception as e:
        return responses.JSONResponse({"details": "{}".format(e)}, status_code=status.HTTP_400_BAD_REQUEST)

    try:
        exisitng_conn = await db.databaseconnection.find_many(where={"user_id": user.id})
        print(exisitng_conn)
    except (errors.PrismaError) as e:
        print(e)
        return


@index_router.post('/query', summary="Query Database with NL")
async def query_database(q: QueryDB, db: DatabaseConnection,
                         current_user: Annotated[QueryResponse,
                                                 Depends(get_current_user)]):
    from prisma import Prisma
    # get connection string from user
    db_conn = await Prisma(datasource={"url": "postgresql://postgres:admin123.@localhost:5433/alx_overflow"}).connect()
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
