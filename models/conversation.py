#!/usr/bin/python
"""Conversation class"""
import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey


class Conversation(BaseModel, Base):
    """Representation of Conversation """
    user_id = Column(String(60), ForeignKey('users.id'), nullable=False)
    prompts_id = Column(Integer, ForeignKey('prompts.id'), nullable=False)

    def __init__(self, *args, **kwargs):
        """initializes Review"""
        super().__init__(*args, **kwargs)
