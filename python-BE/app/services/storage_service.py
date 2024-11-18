import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import logging

# Load environment variables
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize S3 client with credentials
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

def upload_to_s3(file_path: str, bucket_name: str, s3_key: str):
    """
    Upload a file to AWS S3.
    
    Args:
        file_path (str): Path to the file to upload
        bucket_name (str): Name of the S3 bucket
        s3_key (str): The key (path) where the file will be stored in S3
    """
    try:
        # Use bucket name from environment if not provided
        target_bucket = bucket_name or os.getenv('S3_BUCKET_NAME')
        if not target_bucket:
            raise ValueError("No S3 bucket name provided")

        s3_client.upload_file(file_path, target_bucket, s3_key)
        logger.info(f"File {file_path} uploaded to {target_bucket}/{s3_key}")
        
        # Generate a presigned URL for the uploaded file (optional)
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': target_bucket, 'Key': s3_key},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        return presigned_url
        
    except FileNotFoundError:
        logger.error(f"File {file_path} not found")
        raise
    except NoCredentialsError:
        logger.error("AWS credentials not found")
        raise
    except PartialCredentialsError:
        logger.error("Incomplete AWS credentials")
        raise
    except Exception as e:
        logger.error(f"Failed to upload to S3: {str(e)}")
        raise