"""
Scripts to download football data hosted on the website football-data.co.uk
1) football-data.co.uk - Free csv files of football data ranging back to 90s
2) csv url format = https://www.football-data.co.uk/mmz4281/<Season>/E0.csv
 where <Season> = is the concatenation of last 2 years of season start and season end (2223, 2324 etc)
"""

import requests
from io import  StringIO
import pandas as pd
import boto3

def download_epl_data_from_football_data_by_season(season_start: str, season_end: str)-> pd.DataFrame:
    """
    The season_start and season_end will be converted into the concatenation of last 2 years of season start and season
    end (2223, 2324 etc). A request will be made to download the resource. If the resource is not downloaded
    successfully, it will try 2 more times before quitting. If successful, it will convert the request to csv and
    download the file to the S3 bucket

    :param season_start: The string representation of the season start
    :param season_end: The string representation of the season end
    :return: A dataframe containing the data for the specified seaoson
    """


    return season
