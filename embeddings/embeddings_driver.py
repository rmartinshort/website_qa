from website_qa.embeddings.utils import get_embedding
from website_qa.embeddings.constants import RUN_NEW_EMBEDDINGS
import os
from urllib.parse import urlparse
from website_qa.crawler.constants import full_url, datastore_path, processed_data_path
import logging
import openai
import pandas as pd

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


def driver(model_name="text-embedding-ada-002"):

    # need to load API KEY
    with open("website_qa/api_key.txt") as key_file:
        openai.api_key = key_file.read()

    os.environ["OPENAI_API_KEY"] = openai.api_key

    local_domain = urlparse(full_url).netloc

    processed_text_path = os.path.join(
        processed_data_path, local_domain.replace(".", "_")
    )

    if os.path.isfile(
        os.path.join(processed_text_path, "embeddings_and_processed_text.csv")
    ):
        logging.info("Found file with embeddings already created")

    if not RUN_NEW_EMBEDDINGS:
        raise ValueError(
            "Program exits before embedding API calls are made, uncomment if necessary"
        )

    if os.path.isfile(
        os.path.join(processed_text_path, "embedding_ready_processed_text.csv")
    ):
        logging.info("Embedding ready processed text file found")

        embeddings_ready_text = pd.read_csv(
            os.path.join(processed_text_path, "embedding_ready_processed_text.csv")
        )

        # generate embeddings
        logging.info("Generating embeddings,may take a few mins")
        embeddings_ready_text["ada_embedding"] = embeddings_ready_text["text"].apply(
            lambda x: get_embedding(x, model=model_name)
        )

        logging.info("Saving embeddings")
        embeddings_ready_text.to_csv(
            os.path.join(processed_text_path, "embeddings_and_processed_text.csv"),
            index=False,
        )
