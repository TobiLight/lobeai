from enum import Enum
from typing import Union
from fastapi import Form
from pydantic import BaseModel, Field


class QueryDB(BaseModel):
    query: str


class QueryPrompt(BaseModel):
    query: str
    database_id: Union[str, None]

class QueryResponse(BaseModel):
    query: str
    response: str


class DatabaseType(str, Enum):
    PostgreSQL = "postgresql"
    MySQL = "mysql"
    MongoDB = "mongodb"


class DatabaseConnection(BaseModel):
    database_type: DatabaseType
    uri: Union[str, None]
    # username: Union[str, None] = Field(default=None)
    # password: Union[str, None] = Field(default=None)
    # host: Union[str, None] = Field(default=None)
    # port: Union[str, None] = Field(default=None)

    @classmethod
    def as_form(cls, database_type: DatabaseType = Form(...), uri: str = Form(...)):
        return cls(database_type=database_type,
                   uri=uri)

    class Config:
        orm_mode = True
