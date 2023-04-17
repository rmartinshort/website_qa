import pandas as pd
from urllib.parse import urlparse
import os
import tiktoken
from website_qa.preprocessing.utils import remove_newlines, split_into_many
from website_qa.preprocessing.constants import MAX_TOKENS_PER_ROW, TOKENIZER
from website_qa.crawler.constants import full_url, datastore_path, processed_data_path

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


def prepare_for_embedding(df, tokenizer, processed_text_path):
    """

    :param df:
    :param tokenizer:
    :param processed_text_path:
    :return:
    """
    shortened = []

    # Loop through the dataframe
    for row in df.iterrows():

        # If the text is None, go to the next row
        if row[1]['text'] is None:
            continue

        # If the number of tokens is greater than the max number of tokens, split the text into chunks
        if row[1]['n_tokens'] > MAX_TOKENS_PER_ROW:
            shortened += split_into_many(row[1]['text'],tokenizer,max_tokens=MAX_TOKENS_PER_ROW)

        # Otherwise, add the text to the list of shortened texts
        else:
            shortened.append(row[1]['text'])

    df_shortened = pd.DataFrame(shortened, columns=['text'])
    df_shortened['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))
    return df_shortened
    df.to_csv(os.path.join(processed_text_path, "embedding_ready_processed_text.csv"))

def driver():
    """

    :return:
    """

    local_domain = urlparse(full_url).netloc

    raw_text_path = os.path.join(datastore_path,local_domain.replace(".","_"))
    processed_text_path = os.path.join(processed_data_path,local_domain.replace(".","_"))
    # Create a list to store the text files
    texts = []

    # Get all the text files in the text directory
    for file in os.listdir(raw_text_path):
        # Open the file and read the text
        logging.info("Parsing {}".format(file))
        with open(os.path.join(raw_text_path,file), "r", encoding="UTF-8") as f:
            text = f.read()

            # Omit the first 11 lines and the last 4 lines, then replace -, _, and #update with spaces.
            texts.append((file[11:-4].replace('-', ' ').replace('_', ' ').replace('#update', ''), text))

    # Create a dataframe from the list of texts
    df = pd.DataFrame(texts, columns=['fname', 'text'])

    # Set the text column to be the raw text with the newlines removed
    df['text'] = df.fname + ". " + remove_newlines(df.text)
    df.to_csv(os.path.join(processed_text_path,"processed_text.csv"))

    # read in the file
    df = pd.read_csv(os.path.join(processed_text_path,"processed_text.csv"), index_col=0)
    df.columns = ['title', 'text']
    # load the tokenizer
    tokenizer = tiktoken.get_encoding(TOKENIZER)

    # Tokenize the text and save the number of tokens to a new column
    df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))

    logging.info("Generated df: {}".format(df.head()))
    logging.info("Shape of df: {}".format(df.shape))

    # Divide the articles into chunks to that none of them contain too many tokens to be embedded
    df_shortened = prepare_for_embedding(df, tokenizer, processed_text_path)

    df_shortened.to_csv(os.path.join(processed_text_path, "embedding_ready_processed_text.csv"))

    logging.info("Generated shortened df: {}".format(df_shortened.head()))
    logging.info("Shape of shortened df: {}".format(df_shortened.shape))