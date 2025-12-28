import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.pool import QueuePool
from datetime import datetime


# Database configuration
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "linkzap")
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pass")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")

DATABASE_URL = f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    echo=False,  # Set to True for SQL query logging
)

# Create declarative base
Base = declarative_base()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Database session management
def get_db():
    """Dependency for getting database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
