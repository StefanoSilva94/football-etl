class ScraperConstants(object):
    # AWS
    S3_BUCKET_NAME = "football-etl-data-vb2ywa"
    AWS_REGION = "eu-west-2"
    PROFILE_NAME = "football-etl"

    # football-data.o.uk
    FOOTBALL_DATA_URL = "https://www.football-data.co.uk/mmz4281/{season}/E0.csv"
    FOOTBALL_DATA_S3_FILE_KEY = "raw/football_data/{season}.csv"

    # fbref.com
    FBREF_URL = "https://fbref.com/en/comps/9/{year}-{next_year}/schedule/{year}-{next_year}-Premier-League-Scores-and-Fixtures"
    FBREF_DATA_S3_FILE_KEY = "raw/fbref_data/{season_start}-{season_end}.csv"
    FBREF_RAW_METADATA_FILE_KEY = "raw/fbref_data/last_updated.json"