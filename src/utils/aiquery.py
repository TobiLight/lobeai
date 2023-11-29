#!/usr/bin/python3
# File: aiquery.py
# Author: Oluwatobiloba Light

from typing import Dict, List
from src.openai import client
from datetime import datetime
from openai import NotFoundError, APIStatusError, APITimeoutError, \
    InternalServerError, AuthenticationError


def get_applicable_tables_sql(query_text: str, table_meta: List[str]):
    """
    Get applicable tables from database
    """
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                        "content": "You are a helpful assistant that knows a lot about SQL language and manages a database.\nThe database tables are: {}.\n\n Answer only with a comma separated list of tables, without any explanation. Example response: '\"users\", \"products\"'\n\nIf you think there is a table name that can be used but you aren't sure, please include it anyways.".format(table_meta),
            },
            {
                "role": "user",
                "content": "Tell me which tables from the list of tables you would use to make this query:\n{}".format(query_text),
            },
        ]
    )
    return completion.choices[0].message.content


def generate_mongo(query_text: str, table_meta: Dict[str, str]):
    """
    Generates SQL commands based off of user prompt and generated tables.
    """
    queries = client.chat.completions.create(
        model='gpt-4',
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that knows a lot about NoSQL language and manages a MongoDB database. \nYou are using PyMongo (a mongodb python package) as the ODM.\n\n You MUST answer only with a correct PyMongo command query (using the command function pymongo has) and don't wrap it into a code block. Don't include any explanation.\n Today is {0}.\n\n The database tables are: {1}. The table is a hashmap of table name as keys and the schemas as values.".format(datetime.now().date(), table_meta)
            },
            {
                "role": "user",
                "content": "{}".format(query_text),
            },
        ]
    )

    return queries.choices[0].message.content


def generate_sql(query_text: str, table_meta: Dict[str, str], schema: str, db_type: str):
    """
    Generates SQL commands based off of user prompt and generated tables.
    """
    queries = client.chat.completions.create(
        model='gpt-4',
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that knows a lot about SQL language and manages a database. \nYou are using {3} as the database and SQLAlchemy (a python package) as the ORM.\n\n You MUST answer only with a correct SQL query and don't wrap it into a code block. {2} Don't include any explanation.\n Today is {0}.\n\n The database tables are: {1}. The table is a hashmap of table name as keys and the schemas as values.".format(datetime.now().date(), table_meta, schema, db_type)
            },
            {
                "role": "user",
                "content": "{}".format(query_text),
            },
        ]
    )

    return queries.choices[0].message.content


def query_response_to_nl(query_text: str, query_answer: any):
    """"""
    try:
        queries = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You will be given a query and the result of executing the query on a database. Your response should be in HTML syntax explaining the result, note that the results would be set as inner HTML; so it should not include parent tags like DOCTYPE, body, etc. Maximum font size should be 1rem. Also, do not use dark colors.\n\nTry to explain in a detailed manner such that a non tech savvy user would understand, you can try to add tables and charts well formatted in HTML that a user can understand. You can also include any piece of HTML UI that would aid the explanation."
                },
                {
                    "role": "user",
                    "content": "-----------------------------------------\n Query: ${}\n-----------------------------------------\n\nResult: ${}".format(query_text, query_answer),
                },
            ]
        )
    except (NotFoundError, APIStatusError, APITimeoutError,
            InternalServerError, AuthenticationError) as e:
        print(e)

    return queries.choices[0].message.content
