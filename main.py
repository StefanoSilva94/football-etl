# This is a sample Python script.
import boto3
from scrapers.scraper_constants import ScraperConstants as sc
from utils.s3_utils import *
import pandas as pd
import io

if __name__ == '__main__':
    """
    Adhoc script to convert existing csv file into multiple parquet files by gameweek
    Dest = raw/season=2025-2026/gw=01/player_data.parquet
    ...
    Read master csv per season.
    Read the number of gameweeks in the df
    Iterate over the dataframe
    Create a parquet file for each gameweek 
    """


    # Script to run selenium with chromedriver - to test running it in a docker image

    # Get env variable:
    env = is_running_in_aws()

    # Create boto3 session
    if env == "local":
        session = boto3.Session(profile_name=sc.PROFILE_NAME)
    else:
        session = boto3.Session()

    # Initialize S3 client
    s3 = session.client('s3')


    url = "https://fbref.com/en/comps/9/2024-2025/schedule/2024-2025-Premier-League-Scores-and-Fixtures"

    # first load csv data in pandas df

    fb_ref_file_key = sc.FBREF_DATA_S3_FILE_KEY.format(season_start="2024", season_end="2025")
    # get data from S3 bucket
    data = s3.get_object(Bucket=sc.S3_BUCKET_NAME, Key=fb_ref_file_key)

    # Load the data into pandas dataframe
    df = pd.read_csv(io.BytesIO(data['Body'].read()))

    last_gw = df["gameweek"].max()

    # gw_df.to_parquet(fb_ref_file_key, index=False, compression="snappy", partition_cols=["gameweek"])
    #
    # for gw, gw_df in df.groupby("gameweek"):
    #     fb_ref_file_key = f"raw/fbref_data/season=2-2025/gameweek={gw}/players.parquet"
    #     save_pandas_df_to_s3_bucket(s3, gw_df, "parquet", bucket="football-etl-data-vb2ywa", key = fb_ref_file_key)
    #
    for gw in range(1, 39):
        fb_ref_file_key = f"raw/fbref_data/season=2024-2025/gameweek={gw}/players.parquet"
        new_key = f"raw/fbref_data/season=2024-2025/gameweek={gw}/run_id=202601030000/players.parquet"
        rename_file_in_s3(s3, bucket="football-etl-data-vb2ywa", old_key = fb_ref_file_key, new_key=new_key)

    # fb_ref_file_key = f"raw/fbref_data/season=2025-2026/gameweek=15/players_202512082108.parquet"
    # new_key = f"raw/fbref_data/season=2025-2026/gameweek=15/run_id=202512082108/players.parquet"
    # rename_file_in_s3(s3, bucket="football-etl-data-vb2ywa", old_key=fb_ref_file_key, new_key=new_key)
    #
    # fb_ref_file_key = f"raw/fbref_data/season=2025-2026/gameweek=14/players_202512082108.parquet"
    # new_key = f"raw/fbref_data/season=2025-2026/gameweek=14/run_id=202512082108/players.parquet"
    # rename_file_in_s3(s3, bucket="football-etl-data-vb2ywa", old_key = fb_ref_file_key, new_key=new_key)







