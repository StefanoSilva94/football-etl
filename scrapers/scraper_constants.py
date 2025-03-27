class ScraperConstants(object):
    # AWS
    S3_BUCKET_NAME = "football-etl-data-vb2ywa"
    AWS_REGION = "eu-west-2"
    PROFILE_NAME = "football-etl"

    # football-data.o.uk
    FOOTBALL_DATA_URL = "https://www.football-data.co.uk/mmz4281/{season}/E0.csv"
    FOOTBALL_DATA_S3_FILE_KEY = "raw_football_data_{season}"