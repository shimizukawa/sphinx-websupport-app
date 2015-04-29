# -*- coding: utf-8 -*-
"""
    sphinxweb.models
    ~~~~~~~~~~~~~~~~

    Models for the Sphinx web support app.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

from sphinxweb import app

# setup sqlalchemy
engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True)
    moderator = Column(Boolean, default=False)
    email = Column(String(200), unique=True)
    openid = Column(String(200))
    permissions = relationship('Permission', secondary=lambda: userpermissions_table)
    permission_names = association_proxy('permissions', 'name')

    def __init__(self, name, email, openid):
        self.name = name
        self.email = email
        self.openid = openid


class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True)

    def __init__(self, name):
        self.name = name


userpermissions_table = Table('userpermissions', Base.metadata,
    Column('user_id', Integer, ForeignKey("users.id"),
           primary_key=True),
    Column('permission_id', Integer, ForeignKey("permissions.id"),
           primary_key=True)
)


def init_db():
    Base.metadata.create_all(bind=engine)
