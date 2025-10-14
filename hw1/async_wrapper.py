import argparse
import aiohttp
import asyncio
from parsel import Selector
import json
import logging
import task_checker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
                    
logger = logging.getLogger("wrapper")

def arg_parser_setup() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser("A python web scraper/wrapper")
    arg_parser.add_argument("--task", metavar='task.json', help='Specify a task to run' , required=True)
    return arg_parser

async def fetch_page(session, url, xpaths):
    """Async function to fetch a single page"""
    try:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"HTTP Code: {response.status}")
            content = await response.text()
            logger.info(f"Successfully fetched: {url}")
            #query the html with the xpaths
            selector = Selector(text=content)
            results = []
            for i, xpath_family in enumerate(xpaths):
                for xpath in xpath_family:
                    results.extend(selector.xpath(xpath).getall())
                #logger.info(f"XPath results for field {i} on {url}: {results}")
            return {"url": url, "status": response.status, "xpaths": xpaths, "results": results}

    except Exception as e:
        logger.error(f"{e} - {url}")
        return {"url": url, "error": str(e), "xpaths": xpaths}

async def process_pages_as_completed(fetch_tasks):
    """Process pages as they complete, not waiting for all to finish"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page(session, url, xpaths) for url, xpaths in fetch_tasks]
        
        # Process results as they complete
        for coro in asyncio.as_completed(tasks):
            result = await coro  # This only blocks until THIS specific request completes
            if "error" not in result:
                logger.info(f"Processed: {result['url']} - Status: {result['status']}")
                # Process the content and apply XPaths here immediately
            else:
                logger.error(f"Failed: {result['url']} - Error: {result['error']}")

if __name__ == "__main__":
    arg_parser = arg_parser_setup()
    args = arg_parser.parse_args()
    task = None
    with open(args.task,'r') as task_file:
        task = json.load(task_file)
    if not task_checker.check_task(task):
        raise Exception("Task could not be loaded")
    logger.info("Task loaded succesfully")

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
    
    # Process pages as they complete (truly non-blocking)
    asyncio.run(process_pages_as_completed(fetch_tasks))