#!/usr/bin/python3
# File: index.py

from sqlite3 import OperationalError
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, Request, responses
from fastapi import status, responses
from schemas.user import UserProfile
from src.dependencies import get_current_user
from schemas.query import DatabaseConnection, QueryDB, QueryResponse
from src.utils.auth import decode_token
from urllib.parse import urlparse


index_router = APIRouter(responses={404: {"description": "Not Found!"}})


@index_router.get("/", summary="Homepage")
def home():
    return responses.JSONResponse(status_code=status.HTTP_200_OK,
                                  content="Welcome to AI powered E-commerce")
    
@index_router.post("/user")
async def protected_endpoint(token: str):
    print(decode_token(token))
    try:
        user = await get_current_user(token)
    except:
        return {"status": "Could not validate credentials"}
    print(user)
    return {"message": "This is a protected endpoint", "user_id": "user_id"}



@index_router.post("/get-db", summary="Get Database connection string from user")
async def get_dbconn(conn_str: str, request: Request, user: Annotated[UserProfile, Depends(get_current_user)]):
    """"""
    from sqlalchemy import create_engine
    
    token = request.headers.get("Authorization").split()[1]
    user_email = decode_token(token)

    parsed_url = urlparse(conn_str)
    if parsed_url.scheme == 'postgres':
        engine = create_engine("postgresql+psycopg2://{}:{}@{}/{}".format(
            parsed_url.username, parsed_url.password, parsed_url.hostname, parsed_url.path[1:]))
    else:
        engine = create_engine(
            "postgres://lobeai:ZDc2nqiieHWRMszmfgtZVLiyDiVjDNsE@dpg-clghs9ef27hc739kni5g-a.oregon-postgres.render.com/lobeai", echo=True)

    try:
        # Check if the database connection is alive
        engine.connect().close()
        print("Database is connected.")
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")

    conn_params = {
        "username": parsed_url.username,
        "password": parsed_url.password,
        "host": parsed_url.hostname,
        "database": parsed_url.path[1:],
        "scheme": parsed_url.scheme
    }



    # try:
    #     await db_conn.connect()
    #     print("User's Database Connected!")
    #     await db_conn.disconnect()
    # except:
    #     # print("An error has occured")
    #     return {"status": "An error has occured while trying to connect to your database. Please check the connection string and try again"}
    # await client.databaseconnection.create({
    #     "user_id": user_id,
    #     "id": str(uuid4()),
    #     "host": conn_params['host'],
    #     "username": conn_params["username"],
    #     "password": conn_params["password"],
    #     "uri": db_conn,
    #     "port": "5432",
    #     "type": conn_params["scheme"],
    #     "created_at": datetime.now(),
    #     "updated_at": datetime.now()
    # })
    return {"status": "OK"}


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

