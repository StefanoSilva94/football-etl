"""
Scripts to download football data hosted on the website football-data.co.uk
1) football-data.co.uk - Free csv files of football data ranging back to 90s
2) csv url format = https://www.football-data.co.uk/mmz4281/<Season>/E0.csv
 where <Season> = is the concatenation of last 2 years of season start and season end (2223, 2324 etc)
"""

import requests
import boto3
from scraper_constants import ScraperConstants as sc
from boto3.exceptions import Boto3Error
from utils.s3_utils import does_file_exist_in_s3, is_running_in_aws
import logging


def download_epl_data_from_football_data_by_season(season: str, s3_client, overwrite=False):
    """
    1) The season will be formatted into the concatenation of last 2 years of season start and season
    end (2223, 2324 etc). A request will be made to download the resource.
    2) A check will be performed to see if the file already exists, if it does not the script will continue. Since the
    data in these files are static, it wont be necessary to download them multiple times
    3) Send http request for the file
    4) Save the file to the S3 bucket specified

    :param season: The string representation of the season
    :param s3_client: The instance of the S3 bucket the file will be downloaded to
    :param overwrite: Boolean flag to indicate whether to overwrite the existing file on S3 (default is False).
    """

    url = sc.FOOTBALL_DATA_URL.format(season=season)

    try:
        # Download the season data and raise error for non-200 response
        response = requests.get(url)
        response.raise_for_status()

        bucket = sc.S3_BUCKET_NAME
        key = sc.FOOTBALL_DATA_S3_FILE_KEY.format(season=season)

        # Check if the file already exists in S3
        if not overwrite and does_file_exist_in_s3(s3_client=s3_client, bucket=bucket, key=key):
            return
        else:
            # Upload to S3 as a csv File
            s3_client.put_object(
                Bucket=sc.S3_BUCKET_NAME,
                Key=sc.FOOTBALL_DATA_S3_FILE_KEY.format(season=season),
                Body=response.text,
                ContentType = "text/csv"
            )
            print(f"✅ File successfully uploaded to s3://{sc.S3_BUCKET_NAME}/{sc.FOOTBALL_DATA_S3_FILE_KEY.format(season=season)}")


    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download file: {e}")
    except Boto3Error as e:
        print(f"❌ S3 upload failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def increment_current_season(season: str) -> str:
    # Extract the end season as last two digits of string
    end_season = season[2:]

    start_season = end_season

    # Edge case for 2009 -> 2010
    if end_season == "09":
        end_season = "10"
    # Edge case for 1999 -> 2000
    elif end_season == "99":
        end_season = "00"
    # Check if the end season has a leading 0
    elif end_season[0] == "0":
        end_season = "0" + str(int(end_season[1]) + 1)
    else:
        end_season = str(int(end_season) + 1)
    return start_season + end_season

def download_football_data_in_range(s3_client, start_season="9394", end_season="2425"):
    """
    Downloads all football-data files to S3 from the start season to the end season
    :param s3_client: The instance of the S3 bucket the file will be downloaded to
    :param start_season: the season to start downloads from
    :param end_season:  the last season to download data from
    """
    current_season = start_season
    end_season_reached = False
    count = 0

    # Iterate through each season until the end_season_reached flag is updated to True
    while not end_season_reached:
        print(f"Downloading data for season: {current_season}")
        download_epl_data_from_football_data_by_season(current_season, s3_client=s3_client)
        current_season = increment_current_season(current_season)

        if current_season == end_season:
            end_season_reached = True
            print(f"End season reached, exiting loop")
        count += 1
        if count > 40:
            print("Iterations have exceeded number of seasons, exiting loop")
            break



if __name__ == '__main__':
    # Get env variable:
    env = is_running_in_aws()

    # Create boto3 session
    if env == "local":
        session = boto3.Session(profile_name=sc.PROFILE_NAME)
    else:
        session = boto3.Session()

    # Initialize S3 client
    s3 = session.client('s3')

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # download_football_data_in_range(s3, "2324")
    print("Hello football data!")
