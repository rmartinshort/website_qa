import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urlparse
import os
from website_qa.crawler.utils import get_domain_hyperlinks
from website_qa.crawler.constants import full_url, datastore_path, processed_data_path

import logging

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


def crawl(url):
    # Parse the URL and get the domain
    local_domain = urlparse(url).netloc

    # print(local_domain,url)

    # Create a queue to store the URLs to crawl
    queue = deque([url])

    # Create a set to store the URLs that have already been seen (no duplicates)
    seen = set([url])

    # return

    raw_text_path = os.path.join(datastore_path, local_domain.replace(".", "_"))
    processed_text_path = os.path.join(
        processed_data_path, local_domain.replace(".", "_")
    )

    # Create a directory to store the text files
    if not os.path.exists(datastore_path):
        os.mkdir(datastore_path)
    if not os.path.exists(raw_text_path):
        os.mkdir(raw_text_path)

    # Create a directory to store the csv files
    if not os.path.exists(processed_data_path):
        os.mkdir(processed_data_path)
    if not os.path.exists(processed_text_path):
        os.mkdir(processed_text_path)

    # While the queue is not empty, continue crawling
    while queue:
        # Get the next URL from the queue
        url = queue.pop()
        logging.info("Found {}".format(url))  # for debugging and to see the progress

        # Save text from the url to a <url>.txt file
        with open(
            os.path.join(raw_text_path, url[8:].replace("/", "_") + ".txt"),
            "w",
            encoding="UTF-8",
        ) as f:
            # Get the text from the URL using BeautifulSoup
            soup = BeautifulSoup(requests.get(url).text, "html.parser")

            # Get the text but remove the tags
            text = soup.get_text()

            # If the crawler gets to a page that requires JavaScript, it will stop the crawl
            if "You need to enable JavaScript to run this app." in text:
                print(
                    "Unable to parse page " + url + " due to JavaScript being required"
                )

            # Otherwise, write the text to the file in the text directory
            f.write(text)

        # Get the hyperlinks from the URL and add them to the queue
        for link in get_domain_hyperlinks(local_domain, url):
            if link not in seen:
                queue.append(link)
                seen.add(link)


def driver():
    crawl(full_url)
