"""
Database Module Initialization
"""

from .database import Base, SessionLocal, engine
from contextlib import contextmanager

def get_session():
    """
    Get a database session.
    
    Returns:
        Session: A database session
    """
    return SessionLocal()

@contextmanager
def get_db():
    """
    Database session context manager.
    
    Yields:
        Session: A database session
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def initialize_database():
    """
    Initialize the database by creating all tables.
    """
    Base.metadata.create_all(bind=engine)

# Initialize database on module import
initialize_database()