#!/usr/bin/python3
# File: aiquery.py
# Author: Oluwatobiloba Light

from typing import Dict, List
from src.openai import client
from datetime import datetime


def get_applicable_tables(query_text: str, table_meta: List[str]):
    """
    Get applicable tables from database
    """
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                        "content": "You are a helpful assistant that knows a lot about SQL and NoSQL language and manages a database.\nYou are using MongoDB.\nThe database tables are: {}.\n\n Answer only with a comma separated list of tables, without any explanation. Example response: '\"users\", \"products\"'\n\nIf you think there is a table name that can be used but you aren't sure, please include it anyways.".format(table_meta),
            },
            {
                "role": "user",
                "content": "Tell me which tables from the list of tables you would use to make this query:\n{}".format(query_text),
            },
        ]
    )
    return completion.choices[0].message.content


def generate_sql(query_text: str, table_meta: Dict[str, str]):
    """
    Generates SQL commands based off of user prompt and generated tables.
    """
    queries = client.chat.completions.create(
        model='gpt-4',
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that knows a lot about SQL language and manages a database. \nYou are using PostgreSQL as the database and SQLAlchemy as the ORM.\n\n You MUST answer only with a correct SQL query and don't wrap it into a code block. The schema name is 'public'. Don't include any explanation.\n Today is {}.\n\n The database tables are: {}. The table is a hashmap of table name as keys and the schemas as values.".format(datetime.now().date(), table_meta)
            },
            {
                "role": "user",
                "content": "{}".format(query_text),
            },
        ]
    )

    return queries.choices[0].message.content


async def keys_in_tables(tables: str):
    """"""
    from src.db import db
    result = tables.replace("'", "").split(", ")
    data = {}
    for res in result:
        print(res)
        query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = \'public\' AND table_name = \'{res}\';"
        columns = await db.query_raw(query)
        data[res] = columns
    return data


async def keys_in_sql_tables(tables: str):
    """"""
    from src.db import db
    result = tables.replace('"', "").split(", ")
    data = {}
    for res in result:
        query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = \'public\' AND table_name = \'{res}\';"
        columns = await db.query_raw(query)
        data[res] = columns
    return data


def query_response_to_nl(query_text: str, query_answer: any):
    """"""
    queries = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You will be given a query and the result of executing the query on a database. In your response you should include a text explaining the result"
            },
            {
                "role": "user",
                "content": "-----------------------------------------\n Query: ${}\n-----------------------------------------\n\nResult: ${}".format(query_text, query_answer),
            },
        ]
    )

    return queries.choices[0].message.content
