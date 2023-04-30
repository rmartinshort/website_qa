# Regex pattern to match a URL
HTTP_URL_PATTERN = r"^http[s]{0,1}://.+$"

# Define root domain to crawl
domain = "berkeleyca.gov"
full_url = "https://berkeleyca.gov/"
include_htags = ["community-recreation","safety-health","news"]
exclude_htags = ["files","documents",".txt",".pdf"]

datastore_path = "/Users/rmartinshort/Documents/DS_projects/website_qa/text/"
processed_data_path = "/Users/rmartinshort/Documents/DS_projects/website_qa/processed/"
