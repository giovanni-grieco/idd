import argparse
import requests
from lxml import html
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
                    
logger = logging.getLogger("wrapper")

def arg_parser_setup() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser("A python web scraper/wrapper")
    arg_parser.add_argument("--task", metavar='task.json', help='Specify a task to run' , required=True)
    return arg_parser

def check_task(task: dict) -> bool:
    return True

if __name__ == "__main__":
    arg_parser = arg_parser_setup()
    args = arg_parser.parse_args()
    task = None
    with open(args.task,'r') as task_file:
        task = json.load(task_file)
    if not check_task(task):
        raise Exception("Task could not be loaded")
    logger.info("Task loaded succesfully")
