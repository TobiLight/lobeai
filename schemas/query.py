from enum import Enum
from typing import Union
from pydantic import BaseModel, Field

class QueryDB(BaseModel):
    query: str
    
class QueryResponse(BaseModel):
    query: str
    response: str
    

class DatabaseType(str, Enum):
    PostgreSQL = "postgresql"
    MySQL = "mysql"
    MongoDB = "mongodb"
    
class DatabaseConnection(BaseModel):
    database_type: DatabaseType = Field(default=DatabaseType.PostgreSQL)
    uri: Union[str, None] = Field(default=None)
    # username: Union[str, None] = Field(default=None)
    # password: Union[str, None] = Field(default=None)
    # host: Union[str, None] = Field(default=None)
    # port: Union[str, None] = Field(default=None)


