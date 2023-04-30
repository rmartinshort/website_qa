import re
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlparse
from website_qa.crawler.constants import (
    HTTP_URL_PATTERN,
    include_htags,
    exclude_htags,
)
import logging

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


# Create a class to parse the HTML and get the hyperlinks
class HyperlinkParser(HTMLParser):
    """ """

    def __init__(self, include_htags=[], exclude_htags=[]):
        super().__init__()
        # Create a list to store the hyperlinks
        self.hyperlinks = []
        self.include_htags = include_htags
        self.exclude_htags = exclude_htags

    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
        if tag == "a" and "href" in attrs:
            # only append particular types of links
            hlink = attrs["href"]
            if any(item in hlink for item in self.include_htags) and not any(
                item in hlink for item in self.exclude_htags
            ):
                self.hyperlinks.append(hlink)


# Function to get the hyperlinks from a URL
def get_hyperlinks(url):
    """

    :param url:
    :return:
    """
    # Try to open the URL and read the HTML
    try:
        # Open the URL and read the HTML
        with urllib.request.urlopen(url) as response:
            # If the response is not HTML, return an empty list
            if not response.info().get("Content-Type").startswith("text/html"):
                return []

            # Decode the HTML
            html = response.read().decode("utf-8")
    except Exception as e:
        logging.warning(e)
        return []

    # Create the HTML Parser and then Parse the HTML to get hyperlinks
    parser = HyperlinkParser(include_htags=include_htags, exclude_htags=exclude_htags)
    parser.feed(html)

    return parser.hyperlinks


def get_domain_hyperlinks(local_domain, url):
    """

    :param local_domain:
    :param url:
    :return:
    """
    clean_links = []
    for link in set(get_hyperlinks(url)):
        clean_link = None

        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain:
                clean_link = link

        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("/"):
                link = link[1:]
            elif (
                link.startswith("#")
                or link.startswith("mailto:")
                or link.startswith("tel:")
            ):
                continue
            clean_link = "https://" + local_domain + "/" + link

        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))
