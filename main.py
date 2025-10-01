# This is a sample Python script.
import boto3
from scrapers.scraper_constants import ScraperConstants as sc
from utils.s3_utils import rename_file_in_s3, is_running_in_aws
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


if __name__ == '__main__':
    print('Hello World')
    # Script to run selenium with chromedriver - to test running it in a docker image

    # Get env variable:
    env = is_running_in_aws()

    # Create boto3 session
    if env == "local":
        session = boto3.Session(profile_name=sc.PROFILE_NAME)
    else:
        session = boto3.Session()

    # Initialize S3 client
    s3 = session.client('s3')


    url = "https://fbref.com/en/comps/9/2024-2025/schedule/2024-2025-Premier-League-Scores-and-Fixtures"
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # keep it headless if you want
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/116.0.5845.96 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    try:
        driver.get(url)
        html = driver.page_source
        print("✅ Page title is:", driver.title)
        print("✅ Page loaded successfully")
    except Exception as e:
        print("❌ Error:", e)
        print("Why, Why, Why")
    finally:
        driver.quit()

