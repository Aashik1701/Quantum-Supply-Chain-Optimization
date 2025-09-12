"""
Database configuration and session management
"""

import os
from typing import Generator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from models.database import Base


class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        self.database_url = self._get_database_url()
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
        )
    
    def _get_database_url(self) -> str:
        """Get database URL from environment or use SQLite default"""
        # Force SQLite for development to avoid PostgreSQL dependency issues
        db_url = os.getenv('DATABASE_URL')
        if not db_url or 'postgresql' in db_url:
            # Default to SQLite for development
            db_path = os.path.join(
                os.path.dirname(__file__), '..', 'data', 'app.db'
            )
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            db_url = f'sqlite:///{db_path}'
        return db_url
    
    def _create_engine(self):
        """Create SQLAlchemy engine with connection pooling"""
        if self.database_url.startswith('sqlite'):
            # SQLite doesn't support connection pooling
            return create_engine(
                self.database_url,
                echo=os.getenv("DB_ECHO", "").lower() == "true"
            )
        else:
            # PostgreSQL with connection pooling
            return create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=os.getenv("DB_ECHO", "").lower() == "true"
            )
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all database tables (use with caution)"""
        Base.metadata.drop_all(bind=self.engine)


# Global database configuration
db_config = DatabaseConfig()


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = db_config.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create tables"""
    db_config.create_tables()


def reset_db():
    """Reset database - drop and recreate tables"""
    db_config.drop_tables()
    db_config.create_tables()
