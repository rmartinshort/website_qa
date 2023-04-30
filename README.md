# website_qa
Adaptation of openAI website QA tutoral to build a search engine for a website using ADA embeddings for search and ChatGPT to summarize contexts. BBC news is chosen as an example, but the code should be able to handle any website.

Plan is to understand and follow the steps described here, with some minor modifications https://platform.openai.com/docs/tutorials/web-qa-embeddings

### Usage

The main steps taken here are as follows: 
- Crawl a website and download all the pages we hit. This is controlled by the code in crawler and the domain to crawl is in crawler/constants. This could do with more work because much of the data downloaded appears to be junk.    
- Generate embeddings of the downloaded data. First we do some preprocessing to remove unwanted text and break the articles into smaller chunks. This is handled in preprocessing. To generate the embeddings we use "text-embedding-ada-002". This process may take some time depending on the number of articles to be embedded. Note that we don't use a vector database or anything - the embeddings are just stored in csv here.   
- Chat: When a question is asked, it is also embedded with "text-embedding-ada-002" and cosine simialrity is used to extract the top articles for context. Then "gpt-3.5-turbo" is used to generate answers. Langchain is used to streamline this process. This is handled in chat.  

```
from website_qa.chat.chat_driver import driver

driver()

Enter a question (Q to quit):Whats the latest weather report for England

--> An answer should be given 
```

### Initial repo set up with cookiecutter

See https://pypi.org/project/cookiecutter/ for details   
