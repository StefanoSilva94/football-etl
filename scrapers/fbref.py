from datetime import datetime, timedelta
import io
import json
import boto3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from pandas import DataFrame
from scrapers.scraper_constants import ScraperConstants as sc
from utils.s3_utils import save_data_to_s3_bucket_as_csv, is_running_in_aws
from botocore.exceptions import ClientError
from utils.arguments_utils import get_fbref_arguments


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_team_player_data(soup: BeautifulSoup, team: str, home_or_away: str) -> pd.DataFrame:
    """
    Scrape the player data for a specified team. Iterates through all tabs on the tables and extracts all their data
    1) Locates the header for the teams table.
    2) Locates the identifier for each tab (summary, passing, passing_types, etc)
    3) Locates the table body and iterates though the row elements
    4) A data dict is added for each row where the key is the player_name and the value is a dict of the remaining
    column: value pairs
    5) Some older match reports won't have additional tabs, so if this returns none, it will just scrape the summary tab
    :param home_or_away: Takes the value 'home' for a home team and 'away' for an away team. It is used to locate the
    table for the correct team. Home will have index 1, away will have index 0
    :param soup: The soup object to be scraped
    :param team: The name of the team to identify which table to scrape
    :return: Pandas dataframe with the data from the teams table
    """
    # List of the table tabs
    table_tabs = ["summary", "passing", "passing_types", "defense", "possession", "misc"]
    table_headers = [h2 for h2 in soup.find_all("h2") if h2.get_text(strip=True).endswith("Player Stats")]
    if home_or_away == "home":
        table_header = table_headers[0]
    else:
        table_header = table_headers[-1]

    # Dict to store player data in
    data_dict = {}
    # Add the data from each tab in the table to the data-dict - older match reports won't have multiple tabs
    for tab in table_tabs:
        try:

            table = table_header.find_next("table", class_="stats_table", id=lambda x: x and x.endswith(tab))

            if not table:
                logger.info(f"No table found for {tab}. Skipping...")
                continue

            table_body = table.find("tbody")
            table_rows = table_body.find_all("tr") if table_body else []

            for row in table_rows:
                # Get a list of all the cells in the row
                table_cells = row.find_all(["th", "td"])
                if not table_cells:
                    continue

                # Extract player name from the first column
                player_name = row.find(["th", "td"], {"data-stat": "player"}).get_text(strip=True)

                if not player_name:
                    logger.info(f"No player name found for {tab}. Skipping...")

                # Initialize player dict if not in data_dict
                if player_name not in data_dict:
                    data_dict[player_name] = {}


                for cell in table_cells:
                    col = cell["data-stat"]
                    value = cell.get_text(strip=True)

                    # Ignore player column since it is added as a key
                    if col == "player":
                        continue
                    # Store the col value pair in the player data dict if it does not exist already
                    elif col not in data_dict[player_name] or not data_dict[player_name][col]:
                        data_dict[player_name][col] = value

        except Exception as e:
            print(f"Couldn't find element for {tab}, error: {e}")

    # Convert dictionary to DataFrame
    df = pd.DataFrame.from_dict(data_dict, orient="index").reset_index()
    df.rename(columns={"index": "player"}, inplace=True)

    return df


def get_team_name_from_match_report(soup: BeautifulSoup) -> [str]:
    header = soup.find('h1').get_text()
    team_split = header.split('vs.')

    home_team = team_split[0].strip()
    away_team = team_split[1].split('Match Report')[0].strip()

    return [home_team, away_team]


def scrape_match_report_data(match_url: str) -> DataFrame:
    """
    Scrapes the match data from the match report for each player
    1) Extract the team names and date from the header
    2) Extract data for home team players
    3) Extract data for home team goalkeeper
    4) Extract data for the away team players
    5) Extract data for away team goalkeeper
    6) Concatenate the dataframes
    :param match_url: the url for the match report on fbref.com
    :return: A dataframe containing all the data for players on both teams
    """
    df = pd.DataFrame()
    try:
        response = requests.get(match_url)
        if response.status_code != 200:
            time.sleep(300)
            response = requests.get(match_url)

        # Raise error if not 200 status code
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # First extract home team, away team, game week and date
        home_team, away_team = get_team_name_from_match_report(soup)
        logger.info(f"Scraping home team data: {home_team}")
        home_team_data = scrape_team_player_data(soup, home_team, home_or_away="home")
        logger.info(f"Scraping away team data: {away_team}")
        away_team_data = scrape_team_player_data(soup, away_team, home_or_away="away")

        return pd.concat([home_team_data, away_team_data])

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Failed to access match report: {e}")
        return df
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        return df


def extract_table_value_from_row_cell(row, data_stat, is_header=False):
    """
    Extracts text from a table row cell safely.

    :param row: The BeautifulSoup row element.
    :param data_stat: The 'data-stat' attribute to find.
    :param is_header: Boolean indicating if it is a <th> instead of <td>.
    :return: The extracted text or None if not found.
    """
    tag = "th" if is_header else "td"
    cell = row.find(tag, {"data-stat": data_stat})
    return cell.get_text(strip=True) if cell else None


def update_dataframe_with_watermark_columns(row, match_df, columns):
    """
    Updates a dataframe with watermark values from a match row.

    :param row: The BeautifulSoup row element.
    :param match_df: The DataFrame to update.
    :param columns: A list of tuples (column_name, data_stat, is_header).
    :return: Updated DataFrame.
    """
    for col_name, data_stat, is_header in columns:
        match_df[col_name] = extract_table_value_from_row_cell(row, data_stat, is_header)

    return match_df

def scrape_data_in_date_range(season: int, start_date=None, end_date=None):
    """
    This will scrape all data on the fbref scores and fixtures section for a premier league season.
    It will filter for match reports that fall in the range start_date to end_date (inclusive) and it will break the
    loop when it reaches upcoming fixtures (e.g 'Head-to-Head' is shown instead of 'Match Report'
    It will scrape all data within each match report and save it as a csv file to an S3 bucket
    :param season: Season to scrape data from (YYYY)
    :param start_date: start date to scrape data from (inclusive) (In the format YYYY-MM-DD)
    :param end_date: end date t0 scrape data from (inclusive) (In the format YYYY-MM-DD)
    :return:
    """
    logger.info(f"Starting scraper for season: {season} - {season + 1}")
    season_url = sc.FBREF_URL.format(year=season, next_year=season+1)
    df = pd.DataFrame()

    # Default previous date to the start date
    prev_date = start_date
    try:
        time.sleep(5)
        response = requests.get(season_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the match table
        table_header = soup.find("h2")
        match_table = table_header.find_next("tbody")

        if not match_table:
            logging.error("❌ Could not find match table on page.")
            return df

        match_rows = match_table.find_all("tr")
        all_matches = []
        count = 1
        for row in match_rows:
            try:
                # Extract date and match url
                date_str = row.find("td", {"data-stat": "date"}).get_text(strip=True)

                # Update start_date if not specified to be used in the file name
                if not start_date:
                    start_date = date_str

                match_report_link = row.find("td", {"data-stat": "match_report"}).find("a")
                match_report_text = match_report_link.get_text() if match_report_link else None

                # Skip if no match report available
                if not match_report_link:
                    continue

                match_url = "https://fbref.com" + match_report_link["href"]

                # Convert date to datetime format for filtering
                match_date = datetime.strptime(date_str, "%Y-%m-%d")

                # Apply date filtering if needed
                if start_date and match_date < datetime.strptime(start_date, "%Y-%m-%d"):
                    continue
                if end_date and match_date > datetime.strptime(end_date, "%Y-%m-%d"):
                    logger.info(f"Match report date: {match_date} exceeds specified end date: {end_date}")
                    logger.info("Terminating scraper")
                    break
                if match_report_text == "Head-to-Head":
                    logger.info("Match report is not available for the current match")
                    logger.info("Terminating scraper")
                    break

                # Start counting rows from the first match report with a valid date
                logger.info(f"Starting scraper for row: {count}")

                time.sleep(5)
                match_df = scrape_match_report_data(match_url)

                # Scrape the watermark columns and add them to the match_df
                watermark_cols = [
                    ("gameweek", "gameweek", True),  # Found in <th>
                    ("date", "date", False),
                    ("time", "start_time", False),
                    ("home_team", "home_team", False),
                    ("home_xg", "home_xg", False),
                    ("score", "score", False),
                    ("away_xg", "away_xg", False),
                    ("away_team", "away_team", False),
                    ("attendance", "attendance", False),
                    ("referee", "referee", False),
                ]

                match_df = update_dataframe_with_watermark_columns(row, match_df, watermark_cols)
                all_matches.append(match_df)
                logger.info(f"Updated match dataframe {count}")
                count += 1
                prev_date = date_str

            except Exception as e:
                logging.error(f"⚠️ Error processing row: {e}")
                continue
        all_matches_df = pd.concat(all_matches, ignore_index=True) if all_matches else df

        return [all_matches_df, prev_date]

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Failed to access season page: {e}")
        return df


def get_last_updated_data(s3_client):
    """
     Extract the last updated metadata from the json file stored in S3 bucket
     Gets the season and casts to int
     Gets the last_updated string, converts it to a date, adds 1 day, then converts it to a string
    :return: [season, start_date]
    """
    # Read JSON from the S3 bucket
    response = s3_client.get_object(Bucket=sc.S3_BUCKET_NAME, Key=sc.FBREF_RAW_METADATA_FILE_KEY)
    data = json.load(response["Body"])
    season_year = data["season"]

    # Increment the date by 1, convert it to a date, add a day and then cast it to a string
    last_updated_str = data["last_updated"]
    last_updated_date = datetime.strptime(last_updated_str, "%Y-%m-%d")
    last_updated_date += timedelta(days=1)
    start_str = datetime.strftime(last_updated_date, "%Y-%m-%d")

    return [season_year, start_str]


def set_last_updated_data(s3_client, season_year: int, end_date):
    """
    Updates the last updated metadata into the S3 json file
    :param end_date: the date of the most recent game scraped
    :param season_year: start year of the season
    :param s3_client: s3 client instance
    """
    # Dump metadata into json
    data = {
        "season": season_year,
        "last_updated": end_date
    }

    json_data = json.dumps(data)

    s3_client.put_object(
        Bucket=sc.S3_BUCKET_NAME,
        Key=sc.FBREF_RAW_METADATA_FILE_KEY,
        Body=json_data
    )

    logger.info(f"✅ Updated seasons: {season_year}, last updated value = {end_date} in the FBREF meta data file")


def add_scraped_data_to_season_csv(s3_client, season_year:int, scraped_df: pd.DataFrame, update_metadata=True):
    """
    This will take the scraped data in a pandas dataframe and upload it to the corresponding season file in S3
    If the file exists it will read the file into a pandas dataframe and concat it with scraped_df.
    If the file doesn't exist then it will

    :param s3_client: s3 client instance
    :param season_year: YYYY - the starting year of the season
    :param scraped_df: The scraped data due to be added to the dataframe
    :param update_metadata: A boolean flag indicating whether to update the metadata file.
    It should be True for automated scheduling and False for manual runs
    :return: Write the newly scraped data to the season file in S3 bucket
    """
    file_key = sc.FBREF_DATA_S3_FILE_KEY.format(season_start=str(season_year), season_end=str(season_year + 1))

    # See if the file exists already
    try:
        # get data from S3 bucket
        data = s3_client.get_object(Bucket=sc.S3_BUCKET_NAME, Key=file_key)

        # Load the data into pandas dataframe
        df = pd.read_csv(io.BytesIO(data['Body'].read()))
        logger.info(f"Season: {season_year} - {season_year + 1} located successfully")
    except ClientError as e:
        logger.info(f"File does not exist, creating new file: {file_key}")
        df = pd.DataFrame()

    updated_df = pd.concat([df, scraped_df], ignore_index=True)

    save_data_to_s3_bucket_as_csv(s3, updated_df, bucket=sc.S3_BUCKET_NAME, key=sc.FBREF_DATA_S3_FILE_KEY,
                                  season_start=str(season_year), season_end=str(season_year + 1))

    if update_metadata:
        set_last_updated_data(s3_client, season_year, last_match_date)



if __name__ == '__main__':

    """
    Scrape the data in the match report within date range specified
    1) Check if the code is being run locally or via AWS console
    2) Extracts the last updated value from the config file in s3 and starts from the next day
    3) Scrapes all match data from start date for all available fixtures (or until specified end date)
    4) Updates CSV in S3 with the latest data
    """
    print("Hello fbref!")
    # Get env variable:
    env = is_running_in_aws()

    # Create boto3 session
    if env == "local":
        session = boto3.Session(profile_name=sc.PROFILE_NAME)
    else:
        session = boto3.Session()

    # Initialize S3 client
    s3 = session.client('s3')

    season, start_date = get_last_updated_data(s3)
    end_date = None

    # Check if any arguments are passed via command line
    args = get_fbref_arguments()
    if args.season:
        season = args.season
    if args.start_date:
        start_date = args.start_date
    if args.end_date:
        end_date = args.end_date

    metadata_flag = not(args.season or args.start_date or args.end_date)

    # Scrape the data withing the specified range
    season_df, last_match_date = scrape_data_in_date_range(season, start_date=start_date, end_date=end_date)

    # Write the data to csv
    add_scraped_data_to_season_csv(s3, season, season_df, update_metadata=metadata_flag)


