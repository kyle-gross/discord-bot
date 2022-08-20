#!/usr/bin/env python3
from models.base import Base, BaseModel
from sqlalchemy import Column, String


class Guild(Base, BaseModel):

    __tablename__ = 'guild'
    id = Column(String(60), nullable=False, primary_key=True)
    name = Column(String(256), nullable=False)
    def_role = Column(String(256), nullable=True)
    admin_role = Column(String(60), nullable=True)
