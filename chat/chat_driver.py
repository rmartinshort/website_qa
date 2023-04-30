from website_qa.chat.utils import Chatter
import os
import numpy as np
import openai
from urllib.parse import urlparse
from website_qa.crawler.constants import full_url, datastore_path, processed_data_path

import logging
import pandas as pd

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


# example of loading the embeddings and asking a question
# best used in interactive_mode
def driver():

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
        # embeddings df
        logging.info("Loading embeddings")
        df = pd.read_csv(
            os.path.join(processed_text_path, "embeddings_and_processed_text.csv")
        )
        df["ada_embedding"] = df["ada_embedding"].apply(eval).apply(np.array)

        # make chat
        logging.info("Starting chat session")
        chat = Chatter(df)
        chat.interactive()

    else:
        raise ValueError(
            "File {} needs to be generated first before running chat".format(
                os.path.join(processed_text_path, "embeddings_and_processed_text.csv")
            )
        )
