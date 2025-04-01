import boto3
import logging
from botocore.exceptions import NoCredentialsError, ClientError
from scrapers.scraper_constants import ScraperConstants as sc
import pandas as pd
from io import StringIO


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
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            logger.info(f"❌ File: {key} doesn't exist in bucket: {bucket}.")
            return False
        logger.error(f"Error checking file existence: {e}, error_code = {error_code}")
        return False


def save_data_to_s3_bucket_as_csv(s3_client, df,  bucket: str, key: str, **kwargs):
    """
    Uploads a Pandas DataFrame to an S3 bucket as a CSV file.

    :param s3_client: Boto3 S3 client
    :param df: Pandas dataframe to upload as a csv
    :param bucket: Name of the S3 bucket
    :param key: S3 object key with placeholders (e.g., "data/{season}/matches.csv")
    :param kwargs: Additional formatting arguments for the key (e.g., season="2024-25")
    """

    # Store csv in memory buffer
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    # Store in S3
    s3_client.put_object(
        Bucket=bucket,
        Key=key.format(**kwargs),
        Body=csv_buffer.getvalue(),
        ContentType="text/csv"
    )
    formatted_key = key.format(**kwargs)
    logger.info(f"✅ File successfully uploaded to s3://{bucket}/{formatted_key}")


def rename_file_in_s3(s3_client, bucket: str, old_key: str, new_key):
    """
    Rename the object stored in S3
    S3 does not support direct renaming so the file is copied with a new name and then deleted
    :param s3_client: Boto3 S3 client
    :param bucket: Name of the S3 bucket
    :param old_key: The current key used to access the object in S3
    :param new_key: The new key the object is to be renamed to
    """
    try:
        # Copy file with new key
        s3_client.copy_object(
            Bucket=bucket,
            CopySource={'Bucket':bucket, 'Key': old_key},
            Key=new_key
        )
        print(f"✅ File copied to {new_key}")

        # Delete the old file
        s3_client.delete_object(Bucket=bucket, Key=old_key)
        print(f"✅ Old file {old_key} deleted")

    except Exception as e:
        print(f"❌ Error renaming file: {e}")


