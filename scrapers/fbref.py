import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import json
import logging



def scrape_gk_data():
    pass


def scrape_core_match_stats():
    pass


def scrape_team_player_data(soup: str, team: str) -> pd.DataFrame:
    """
    Scrape the player data for a specified team. Iterates through all tabs on the tables and extracts all their data
    1) Locates the header for the teams table.
    2) Locates the identifier for each tab (summary, passing, passing_types, etc)
    3) Locates the table body and iterates though the row elements, saving the data to a dataframe
    4) Some older match reports won't have additional tabs, so if this returns none, it will just scrape the summary tab
    :param soup: The soup object to be scraped
    :param team: The name of the team to identify which table to scrape
    :return: Pandas dataframe with the data from the teams table
    """
    # List of the table tabs
    table_tabs = ["summary", "passing", "passing_types", "defensive_actions", "possession", "misc"]
    table_header = soup.find("h2", string=f"{team} Player Stats")
    for tab in table_tabs:
        try:
            table_rows = (table_header
                              .find_next("table", class_="stats_table", id=lambda x: x and x.endswith(tab))
                              .find_next("tbody"))


        except Exception as e:
            print(f"Couldn't find element for {tab}, error: {e}")
            try:
                if tab == "summary":
                    table_rows = table_header.find_next("tbody")
            except Exception as e:
                print(f"Couldn't find element for {tab}, error: {e}")



def scrape_match_report_data(match_url: str) -> pd.DataFrame:

    # First extract home team, away team, game week and date
    # home_team, away_team, gw, date = scrape_core_match_stats()

    # Scrape home team data
    # scrape_gk_data()

    # Scrape away team data
    # scrape_team_player_data()
    # scrape_gk_data()

    try:
        response = requests.get(match_url)
        if response.status_code != 200:
            time.sleep(300)
            response = requests.get(match_url)

        # Raise error if not 200 status code
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        scrape_team_player_data(soup, "Burnley")


    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Failed to download file: {e}")
        return
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        return




if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # scrape_match_report_data("https://fbref.com/en/matches/3a6836b4/Burnley-Manchester-City-August-11-2023-Premier-League")
    scrape_match_report_data("https://fbref.com/en/matches/15ef0a23/Chelsea-Hull-City-August-15-2009-Premier-League")