#!/usr/bin/env python3
from models.base import Base, BaseModel
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql.schema import ForeignKey

class DefCall(BaseModel, Base):

    __tablename__ = 'defense'
    id = Column(String(60), nullable=False, primary_key=True)
    name = Column(String(256), nullable=False)
    troops = Column(Integer, nullable=False)
    time = Column(DateTime, nullable=False)
    link = Column(String(562), nullable=False)
    guild_id = Column(String(60), ForeignKey('guild.id', ondelete='CASCADE'), nullable=False)
