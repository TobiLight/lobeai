#!/usr/bin/python3
""" holds class User"""

from models.base_model import BaseModel, Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class User(BaseModel, Base):
    """Representation of a user """
    email = Column(String(128), nullable=False)
    password = Column(String(128), nullable=False)
    name = Column(String(128), nullable=True)
    conversations = relationship("Conversation", backref="user")
    reviews = relationship("Review", backref="user")
