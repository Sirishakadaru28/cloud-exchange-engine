import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase):
    pass

engine = None
SessionLocal = None

def get_database_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not configured.")
    return url

def get_engine():
    global engine
    if engine is None:
        engine = create_engine(get_database_url(), pool_pre_ping=True, pool_recycle=300)
    return engine

def get_session_factory():
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
    return SessionLocal

def create_tables():
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=get_engine())
