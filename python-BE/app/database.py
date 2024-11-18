from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:8895@localhost:5432/document_management"

try:
    engine = create_engine(
        DATABASE_URL,
        echo=True,  # Set to False in production
        pool_pre_ping=True
    )
except Exception as e:
    logger.error(f"Error creating engine: {str(e)}")
    raise

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test connection function
def test_connection():
    try:
        with engine.connect() as conn:
            logger.info("Successfully connected to the database!")
        return True
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False