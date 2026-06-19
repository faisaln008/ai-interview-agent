import os
import uuid

from sqlalchemy import create_engine, Column, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker

# Resolve the database URL. Fall back to a local SQLite file for dev so that
# no PostgreSQL installation is required locally.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")

# Railway (and some other providers) inject a "postgres://" URL, but SQLAlchemy
# requires the "postgresql://" prefix.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs this flag when used with FastAPI's threaded request handling.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, index=True, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


def init_db():
    """Create all tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
