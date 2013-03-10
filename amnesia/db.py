# -*- coding: utf-8 -*-

from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

__all__ = ['engine', 'Session', 'meta']

engine = None
Session = scoped_session(sessionmaker(autoflush=True, autocommit=False))
meta = MetaData()
