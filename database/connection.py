import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Default to SQLite for local development, support PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///pathfinder.db")

# SQLite needs special arguments for thread safety during local development
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency injection generator to retrieve db session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
