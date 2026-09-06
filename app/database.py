import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured. Add a PostgreSQL DATABASE_URL environment variable."
    )

# Neon provides a standard PostgreSQL URL. This project uses psycopg 3,
# so explicitly select the psycopg SQLAlchemy dialect instead of the legacy
# psycopg2 dialect that SQLAlchemy 2.0 uses for postgresql:// URLs.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgres://") :]
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgresql://") :]
elif DATABASE_URL.startswith("postgresql+psycopg2://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgresql+psycopg2://") :]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def create_tables():
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
