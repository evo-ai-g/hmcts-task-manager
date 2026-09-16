from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# SQLite needs check_same_thread=False so FastAPI can use it across threads.
# Other databases (Postgres, MySQL) don't take this argument at all.
connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class every ORM model inherits from."""


def get_db():
    """FastAPI dependency: yield a DB session, close it when the request ends."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
