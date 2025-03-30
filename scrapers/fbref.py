import os
from typing import Type

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import json
import logging

from pandas import DataFrame


def scrape_gk_data():
    pass


def scrape_core_match_stats():
    pass


def scrape_team_player_data(soup: BeautifulSoup, team: str) -> pd.DataFrame:
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
    table_tabs = ["summary", "passing", "passing_types", "defense", "possession", "misc"]
    table_header = soup.find("h2", string=f"{team} Player Stats")
    for tab in table_tabs:
        try:
            table_rows = (table_header
                          .find_next("table", class_="stats_table", id=lambda x: x and x.endswith(tab))
                          .find_next("tbody"))


        except Exception as e:
            print(f"Couldn't find element for {tab}, error: {e}")


def get_team_name_from_match_report(soup: BeautifulSoup) -> [str]:
    header = soup.find('h1').get_text()
    team_split = header.split('vs.')

    home_team = team_split[0].strip()
    away_team = team_split[1].split('Match Report')[0].strip()

    return [home_team, away_team]


def scrape_match_report_data(match_url: str) -> Type[DataFrame]:
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
    df = pd.DataFrame
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
        home_team_data = scrape_team_player_data(soup, home_team)
        away_team_data = scrape_team_player_data(soup, away_team)

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Failed to access match report: {e}")
        return df
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        return df


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # scrape_match_report_data("https://fbref.com/en/matches/3a6836b4/Burnley-Manchester-City-August-11-2023-Premier-League")
    scrape_match_report_data("https://fbref.com/en/matches/15ef0a23/Chelsea-Hull-City-August-15-2009-Premier-League")
