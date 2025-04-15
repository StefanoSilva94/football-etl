# This is a sample Python script.
import boto3
from scrapers.scraper_constants import ScraperConstants as sc
from utils.s3_utils import rename_file_in_s3, is_running_in_aws


# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

# Press the green button in the gutter to run the script.
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

    for file in content:
        file_name = file["Key"]
        updated_file_name_prefix = file_name.replace("raw_", "raw/")
        updated_file_name = updated_file_name_prefix.replace("data_", "data/")
        rename_file_in_s3(s3, sc.S3_BUCKET_NAME, file_name, updated_file_name)

