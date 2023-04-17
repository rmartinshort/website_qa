# Regex pattern to match a URL
HTTP_URL_PATTERN = r"^http[s]{0,1}://.+$"

# Define root domain to crawl
domain = "bbc.co.uk"
full_url = "https://www.bbc.co.uk/news/"
include_htags = ["news"]
exclude_htags = []

datastore_path = "/Users/rmartinshort/Documents/DS_projects/website_qa/text/"
processed_data_path = "/Users/rmartinshort/Documents/DS_projects/website_qa/processed/"
