# Scrapers

### Overview
Scrapers have been built to scrape data from multiple sources.  Below is a high level summary of how the scrapers work.
---
### General Setup
1. Each scraper is container in a dedicated Python file within the scrapers package: **`/scrapers/<scraper>.py`**
2. The data is stored as parquet files in AWS S3
3. Constants are managed in the scrapers package **`/scrapers/scraper_constants.py`**. This contains information for the
website urls and S3 bucket information
4. Metadata is stored in the last_updated.json file to track the last time the scrape as successfully run

### FBRef.com

1. The template url for scraping = "https://fbref.com/en/comps/9/{year}-{next_year}/schedule/{year}-{next_year}-Premier-League-Scores-and-Fixtures"

2. The scraper expects 3 inputs:
    - `season`: The starting year of the season to scrape season to scrape, e.g. 2025
    - `start_date`: Start date in YYYY-MM-DD
    - `end_date`: End date in YYYY-MM-DD (or leave blank to scrape all data from the start date)
3. The inputs will automatically be read from the last_updated.json file. This is automatically updated after every run.
However, the inputs can be overwritten by passing the arguments via the command line:    
`fbref.py --start_date 2025-05-11 --end_date 2025-05-17`
4. Data is scraped using the function `scrape_data_in_date_range`, this will scrape all the data from the specified 
start_date to the specified end_date and return it in a pandas dataframe. Note: this will try to access the web page 
using the requests library first, if this does not return 200 response selenium is used as a fail-safe
5. The function `add_scraped_data_to_gw_as_parquet` is used to upload the scraped data to S3 as parquet files,
partitioned by **season**, **gameweek** and **run_id**.
    - Since a gameweek can span over multiple days, the scraper might be run multiple times per gamerweek, so a run_id 
    is used to differentiate runs
6. Upon successfully scraping a _success file is added to each successuful run and the last_updated.json file is updated
