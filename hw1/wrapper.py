import argparse
import requests
from lxml import html
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

if __name__ == "__main__":
    arg_parser = arg_parser_setup()
    args = arg_parser.parse_args()
    task = None
    with open(args.task,'r') as task_file:
        task = json.load(task_file)
    if not task_checker.check_task(task):
        raise Exception("Task could not be loaded")
    logger.info("Task loaded succesfully")


    #itero sulle risorse, gli applico i vari XPATH per quel dominio
    schema = task["schema"]
    domain_keys = [key for key in task.keys() if key != "schema"]
    for domain_key in domain_keys:
        xpaths = task[domain_key]['xpaths']
        page_urls = task[domain_key]['pages']
        for page_url in page_urls:
            try:
                page_url = domain_key+page_url
                response = requests.get(page_url)
                if response.status_code != 200:
                    raise Exception(f"HTTP Code: {response.status_code}")
                print(response.status_code)
                #print(response.text)
            except Exception as e:
                logger.error(f"{e} - {page_url}")
