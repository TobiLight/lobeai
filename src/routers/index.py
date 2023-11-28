#!/usr/bin/python3
# File: index.py
# Author: Oluwatobiloba Light

from sqlite3 import OperationalError
from fastapi import APIRouter, Depends, HTTPException, responses
from fastapi import status, responses
from schemas.user import UserProfile
from schemas.query import DatabaseConnection
from src.utils.auth import custom_auth
from urllib.parse import urlparse
from google.auth.transport import requests
from src.db import db
from uuid import uuid4
from prisma import errors

google_request = requests.Request()


index_router = APIRouter(
    responses={404: {"description": "Not Found!"}}, tags=["Database"])


@index_router.get("/", summary="Homepage")
def home():
    return responses.JSONResponse(status_code=status.HTTP_200_OK,
                                  content="Welcome to AI powered E-commerce")


@index_router.post("/create-db", summary="Create a Database connection\
    from user")
async def create_dbconn(db_conn: DatabaseConnection,
                        user: UserProfile = Depends(custom_auth)):
    """"""
    from sqlalchemy import create_engine

    parsed_url = urlparse(db_conn.uri)

    existing_conn = await db.databaseconnection.\
        find_first(where={"uri": db_conn.uri})
    if existing_conn:
        return {"status": "Database connection exists already!", "data": {
            "id": existing_conn.id,
            "uri": existing_conn.uri
        }}

    if db_conn.database_type != 'mongodb' and (not parsed_url.hostname
                                               or not parsed_url.path[1:] or
                                               parsed_url.path[1:] == ''):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid Database URI")
    print(parsed_url.hostname, parsed_url.path[1:])
    if db_conn.database_type == 'mongodb' and (not parsed_url.hostname):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid Database URI")
    if db_conn.database_type == 'postgresql':
        engine = create_engine(
            "postgresql+psycopg2://{}:{}@{}:{}/{}".
            format(parsed_url.username, parsed_url.password,
                   parsed_url.hostname,
                   parsed_url.port, parsed_url.path[1:]), echo=True)
    elif db_conn.database_type == 'mysql':
        engine = create_engine(
            "mysql+mysqldb://{}:{}@{}:{}/{}".
            format(parsed_url.username, parsed_url.password,
                   parsed_url.hostname,
                   parsed_url.port, parsed_url.path[1:]), echo=True)
    else:
        # handle mongodb connection here
        from pymongo.mongo_client import MongoClient

        client_mongo = MongoClient(db_conn.uri)
        if not client_mongo.is_mongos:
            print("Connected to a standalone MongoDB server")

        # Check if connected to a primary node in a replica set
        if client_mongo.is_primary:
            print("Connected to the primary node in a replica set")

        new_db_conn = await db.databaseconnection.create({
            "id": str(uuid4()),
            "user_id": user["id"],
            "uri": parsed_url.geturl(),
            "type": db_conn.database_type,
            "database_name": db_conn.database_name
        })
        client_mongo.close()
        return {"status": "OK", "data": {
            "id": new_db_conn.id,
            "uri": new_db_conn.uri,
            "database_name": new_db_conn.database_name
        }}

    try:
        engine.connect().close()
        print("Database is connected.")
        new_db_conn = await db.databaseconnection.create({
            "id": str(uuid4()),
            "user_id": user["id"],
            "uri": parsed_url.geturl(),
            "type": db_conn.database_type
        })
    except (errors.PrismaError, OperationalError) as e:
        print(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="{}".format(e))

    return {"status": "Ok", "data": {
            "id": new_db_conn.id,
            "uri": new_db_conn.uri
            }}


@index_router.get("/get-db", summary="Get Database Connection URI")
async def get_dbconn(user: UserProfile = Depends(custom_auth)):
    """"""
    try:
        existing_conn = await db.databaseconnection.\
            find_many(where={"user_id": user["id"]})
    except (errors.PrismaError) as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="{}".format(e))
    return {"status": "Ok", "data": [*existing_conn]}
