import argparse

def get_fbref_arguments():
    parser = argparse.ArgumentParser(description="Run FBRef scraper.")
    parser.add_argument("--season", type=int, help="Season year, e.g. 2024")
    parser.add_argument("--start_date", type=str, help="Start date in YYYY-MM-DD")
    parser.add_argument("--end_date", type=str, help="End date in YYYY-MM-DD")
    return parser.parse_args()