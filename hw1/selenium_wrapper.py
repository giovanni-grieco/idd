import argparse
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from parsel import Selector
import json
import logging
import task_checker
from concurrent.futures import ThreadPoolExecutor
import threading

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
                    
logger = logging.getLogger("wrapper")

def arg_parser_setup() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser("A python web scraper/wrapper")
    arg_parser.add_argument("--task", metavar='task.json', help='Specify a task to run' , required=True)
    arg_parser.add_argument("--headless", action='store_true', help='Run browser in headless mode')
    return arg_parser

def create_driver(headless=True):
    """Create a Chrome WebDriver instance"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Use webdriver-manager to automatically download and manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

def fetch_page_selenium(url, xpaths, headless=True):
    """Fetch a single page using Selenium and return the result"""
    driver = None
    try:
        driver = create_driver(headless)
        logger.info(f"Loading page: {url}")
        driver.get(url)
        
        # Wait for the page to load - you might need to adjust this selector
        # for Google Finance, wait for price elements to be present
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-last-price], .YMlKec, .P6K39c"))
            )
        except TimeoutException:
            logger.warning(f"Timeout waiting for content to load on {url}")
        
        # Get the page source after JavaScript execution
        content = driver.page_source
        
        # Query the HTML with the XPaths
        selector = Selector(text=content)
        results = []
        for i, xpath_family in enumerate(xpaths):
            field_results = []
            for xpath in xpath_family:
                xpath_results = selector.xpath(xpath).getall()
                field_results.extend(xpath_results)
            results.append(field_results)
            logger.info(f"XPath results for field {i} on {url}: {field_results}")
        
        logger.info(f"Successfully fetched: {url}")
        return {"url": url, "status": 200, "xpaths": xpaths, "results": results}

    except WebDriverException as e:
        logger.error(f"WebDriver error on {url}: {e}")
        return {"url": url, "error": f"WebDriver error: {str(e)}", "xpaths": xpaths}
    except Exception as e:
        logger.error(f"Error on {url}: {e}")
        return {"url": url, "error": str(e), "xpaths": xpaths}
    finally:
        if driver:
            driver.quit()

async def process_pages_async(fetch_tasks, headless=True, max_workers=3):
    """Process pages using ThreadPoolExecutor with Selenium"""
    loop = asyncio.get_event_loop()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks to the thread pool
        futures = [
            loop.run_in_executor(executor, fetch_page_selenium, url, xpaths, headless)
            for url, xpaths in fetch_tasks
        ]
        
        # Process results as they complete
        for future in asyncio.as_completed(futures):
            result = await future
            if "error" not in result:
                logger.info(f"Processed: {result['url']} - Status: {result['status']}")
                # Process the results here
                yield result
            else:
                logger.error(f"Failed: {result['url']} - Error: {result['error']}")
                yield result

if __name__ == "__main__":
    arg_parser = arg_parser_setup()
    args = arg_parser.parse_args()
    task = None
    with open(args.task,'r') as task_file:
        task = json.load(task_file)
    if not task_checker.check_task(task):
        raise Exception("Task could not be loaded")
    logger.info("Task loaded successfully")

    schema = task["schema"]
    domain_keys = [key for key in task.keys() if key != "schema"]
    
    # Collect all URLs to fetch
    fetch_tasks = []
    for domain_key in domain_keys:
        xpaths = task[domain_key]['xpaths']
        page_urls = task[domain_key]['pages']
        for page_url in page_urls:
            full_url = domain_key + page_url
            fetch_tasks.append((full_url, xpaths))
    
    async def main():
        async for result in process_pages_async(fetch_tasks, headless=args.headless, max_workers=2):
            if "error" not in result:
                print(f"Results from {result['url']}: {result['results']}")
    
    # Process pages as they complete
    asyncio.run(main())