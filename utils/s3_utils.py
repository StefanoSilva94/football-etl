import boto3
import logging

import pandas as pd
from botocore.exceptions import NoCredentialsError, ClientError


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def does_file_exist_in_s3(s3_client, bucket: str, key: str) -> bool:
    """
    Check if a file exists in a s3 bucket
    :param s3_client: The S3 client used to interact with the S3 bucket
    :param bucket: Name of the S3 bucket
    :param key: Path of the file in the bucket
    :return: True if the file exists, otherwise False
    """
    try:
        # Try and access the file and return True if it exists
        s3_client.head_object(Bucket=bucket, Key=key)
        logger.info(f"✅ File: {key} exists in bucket: {bucket}.")
        return True

    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logger.info(f"❌ File: {key} doesn't exist in bucket: {bucket}.")
            return False
        logger.error(f"Error checking file existence: {e}")
        return False



