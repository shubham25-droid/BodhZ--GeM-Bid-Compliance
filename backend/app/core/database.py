from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create database engine
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, echo=False)

# Session factory for DB transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for ORM models
Base = declarative_base()


# --------------------------------------------------
# DATABASE DEPENDENCY INJECTOR
# --------------------------------------------------
def get_db():
    """
    FastAPI dependency yielding a database session per request
    and closing it automatically after the response.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
