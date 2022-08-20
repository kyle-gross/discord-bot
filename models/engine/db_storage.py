#!/usr/bin/env python3
from models.base import Base
import os
from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')


class DBStorage():

    __engine = None
    __session = None

    def __init__(self):
        self.__engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

    def new(self, obj):
        """Adds object to current database session"""
        self.__session.add(obj)

    def save(self):
        """Saves current database session"""
        self.__session.commit()

    def delete(self, obj):
        """Deletes object from current database session"""
        self.__session.delete(obj)

    def close(self):
        """Call remove() method on private session attribute"""
        self.__session.close()

    def reload(self):
        """Creates all tables in database"""
        from sqlalchemy.orm import sessionmaker, scoped_session
        from sqlalchemy.orm.session import Session

        Base.metadata.create_all(self.__engine)
        session_factory = sessionmaker(
            bind=self.__engine, expire_on_commit=False, autocommit=False
        )
        Session = scoped_session(session_factory)
        self.__session = Session()
