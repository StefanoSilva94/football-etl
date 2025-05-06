import pytest
from unittest.mock import Mock, patch
from scrapers.fbref import scrape_match_report_data, scrape_data_in_date_range
import pandas as pd
from pandas.testing import assert_frame_equal
import numpy as np
import pdb
import os
from schemas.pandas_schemas import FbRefSchema

@pytest.fixture(autouse=True)
def fast_sleep():
    with patch("time.sleep", return_value=None):
        yield

@pytest.fixture
def mock_new_vs_for_match_report():
    """Mock the requests.get response to return sample HTML.
    response = requests.get(match_url)"""

    file_path = "tests/test_files/new_vs_nott_for_22_23.html"
    with open(file_path, "r", encoding="utf-8") as f:
        new_vs_for_html = f.read()

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.content = new_vs_for_html.encode("utf-8")  # Encode as bytes
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_2024_2025_scores_and_fixtures():
    """
    Reads the html content from the test files folder and mocks a requests.get to return the scores and fixtures html
    """
    # Read the scores and fixtures html locally
    with open("tests/test_files/scores_and_fixtures_2025_05_06.html", "r") as f:
        scores_and_fixtures_html = f.read()

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.content = scores_and_fixtures_html.encode("utf-8")  # Encode as bytes
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_scrape_match_report():
    dummy_df = pd.DataFrame({"player": ["Test"], "stat": [1]})
    with patch("scrapers.fbref.scrape_match_report_data", return_value=dummy_df):
        yield

def test_scrape_match_report_data(mock_new_vs_for_match_report):
    """
    Testing that the scraper correctly scrapes the data in the Newcastle vs Nottingham Forrest game
    """
    fbRefSchema = FbRefSchema()

    result_df = scrape_match_report_data("dummy_url")
    exp_df = pd.read_csv("tests/test_files/new_vs_nott_for_22_23.csv", dtype=fbRefSchema.get_schema())

    # Empty cells are read as an empty string, convert these to null
    result_df.replace("", np.nan, inplace=True)

    # Reset the index of both dataframes to ensure they have a consistent range-based index
    exp_df.reset_index(drop=True, inplace=True)
    result_df.reset_index(drop=True, inplace=True)

    # Iterate over each column
    for column in exp_df.columns:
        exp_type = exp_df[column].dtype
        result_type = result_df[column].dtype

        # Check if the data types are different
        if exp_type != result_type:
            print(f"Column: {column}")
            print(f"exp_df data type: {exp_type}")
            print(f"result_df data type: {result_type}")
            print("-----------")

    # Use to debug values of failed test
    # pdb.set_trace()

    # Reset the index of both dataframes to ensure they have a consistent range-based index
    assert_frame_equal(result_df, exp_df, check_dtype=False, check_like=True)




def test_scraper_updates_last_updated_value_correctly(mock_2024_2025_scores_and_fixtures, mock_scrape_match_report):
    """
    With a specified start date and no end date, verify that the scraper exits for games that have not been played yet
    (no match report available) and that the last_updated value is correct.
    This is not concerned with what the scraped data returns, this is focused on the last_updated value being correctly.
    This will use the scores and fixtures hml from the 2024/2025 season as of 06th May.
    It will specify a start date of 2025-05-04. It should return last_updated date as 2025-05-05
    populated in the metadata file
    :param mock_request:
    :return:
    """

    # Create the mock request to the scores and fixtures page
    # scrape_data_in_date_range returns [dataframe, last_updated]
    result_last_updated = scrape_data_in_date_range(season=2025, start_date="2025-05-04", end_date=None)[1]
    exp_last_updated = "2025-05-05"

    assert result_last_updated == exp_last_updated

