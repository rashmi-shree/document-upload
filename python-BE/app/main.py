from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import boto3
from botocore.exceptions import NoCredentialsError
import logging
from app.database import DATABASE_URL, test_connection
from app.models import Base, User, Document
from app.routers import auth, documents

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def test_aws_connection():
    try:
        s3 = boto3.client('s3')
        buckets = s3.list_buckets()
        bucket_names = [bucket['Name'] for bucket in buckets['Buckets']]
        return {
            "status": "success",
            "message": "AWS Connection Successful!",
            "buckets": bucket_names
        }
    except Exception as e:
        logger.error(f"AWS Connection Failed: {str(e)}")
        return {
            "status": "error",
            "message": f"AWS Connection Failed: {str(e)}"
        }

# Initialize database and AWS
@app.on_event("startup")
async def startup_event():
    # Check database connection
    engine = create_engine(DATABASE_URL)
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
        
        # Check AWS credentials
        aws_status = test_aws_connection()
        if aws_status["status"] == "error":
            logger.error(aws_status["message"])
            raise Exception(aws_status["message"])
        else:
            logger.info("AWS credentials verified successfully!")
            
    except SQLAlchemyError as db_error:
        logger.error(f"Database connection error: {str(db_error)}")
        raise
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise
    finally:
        engine.dispose()

# Root endpoint
@app.get("/")
def read_root():
    # Check both database and AWS connections
    db_status = "Connected" if test_connection() else "Not Connected"
    aws_test = test_aws_connection()
    
    return {
        "status": "Server is running",
        "database_connection": db_status,
        "aws_connection": aws_test
    }

# Test endpoint for AWS connection (remove in production)
@app.get("/test-aws/", tags=["Testing"])
async def test_aws():
    return test_aws_connection()

# Include the routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])