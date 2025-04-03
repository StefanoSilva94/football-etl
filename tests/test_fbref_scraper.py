import pytest
from unittest.mock import Mock, patch
from scrapers.fbref import scrape_match_report_data
import pandas as pd
import os

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
    """Mock the requests.get response to return sample HTML."""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.content = sample_html.encode("utf-8")  # Encode as bytes
        mock_get.return_value = mock_response
        yield mock_get

def test_scrape_match_report_data(mock_request):
    """
    Tests that the match report data is correctly scraped for Newcastle vs Forest in 22/23 season.
    """
    result_df = scrape_match_report_data("dummy_url")
    exp_df = pd.read_csv("tests/test_files/new_vs_nott_for_22_23.html")
    assert result_df.equals(exp_df)
