#!/usr/bin/env python3
from models.base import Base, BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import ForeignKey

class Artifact(BaseModel, Base):
    __tablename__ = 'artifacts'
    id = Column(String(60), nullable=False, primary_key=True)
    name = Column(String(256), nullable=False)
    hours = Column(Integer, nullable=False)
    current_owner = Column(String(60), nullable=True)
    guild_id = Column(String(60), ForeignKey('guild.id', ondelete='CASCADE'), nullable=False)
