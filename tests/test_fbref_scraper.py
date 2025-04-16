import pytest
from unittest.mock import Mock, patch
from scrapers.fbref import scrape_match_report_data
import pandas as pd
from pandas.testing import assert_frame_equal
import numpy as np
import pdb
import os
from schemas.pandas_schemas import FbRefSchema

@pytest.fixture
def sample_html():
    """Reads the test HTML file and returns its content as a string."""
    print("Current working directory:", os.getcwd())
    file_path = "tests/test_files/new_vs_nott_for_22_23.html"
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()
    return html_content

@pytest.fixture
def mock_request(sample_html):
    """Mock the requests.get response to return sample HTML.
    response = requests.get(match_url)"""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.content = sample_html.encode("utf-8")  # Encode as bytes
        mock_get.return_value = mock_response
        yield mock_get


def test_scrape_match_report_data(mock_request):
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