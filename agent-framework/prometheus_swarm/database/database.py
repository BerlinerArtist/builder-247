"""
Database Configuration and Session Management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool
import os

# Determine database path
db_path = os.environ.get('DATABASE_URL', 'sqlite:///prometheus_swarm.db')

# Create Engine
engine = create_engine(
    db_path, 
    connect_args={'check_same_thread': False},  # For SQLite
    poolclass=StaticPool  # Use a static connection pool
)

# Create Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Declarative Base
class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models"""
    pass