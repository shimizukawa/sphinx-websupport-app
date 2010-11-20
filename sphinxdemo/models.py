# -*- coding: utf-8 -*-
"""
    sphinxdemo.models
    ~~~~~~~~~~~~~~~~~

    Models for the Sphinx web support demo webapp.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sphinxdemo import app

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

    def __init__(self, name, email, openid):
        self.name = name
        self.email = email
        self.openid = openid


def init_db():
    Base.metadata.create_all(bind=engine)
