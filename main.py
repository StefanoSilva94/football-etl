# This is a sample Python script.
import boto3
from scrapers.scraper_constants import ScraperConstants as sc
from utils.s3_utils import rename_file_in_s3, is_running_in_aws


if __name__ == '__main__':
    print('Hello World')

    # Get env variable:
    env = is_running_in_aws()

    # Create boto3 session
    if env == "local":
        session = boto3.Session(profile_name=sc.PROFILE_NAME)
    else:
        session = boto3.Session()

    # Initialize S3 client
    s3 = session.client('s3')

    response =  s3.list_objects(
        Bucket=sc.S3_BUCKET_NAME,
    )
    content = response["Contents"]

    rename_file_in_s3(s3, sc.S3_BUCKET_NAME, "raw/fbref_data/2022-08-05_2023-05-28.csv", "raw/fbref_data/2022-2023.csv")


