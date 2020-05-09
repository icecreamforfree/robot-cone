from algoliasearch.search_client import SearchClient
import os
from dotenv import load_dotenv
load_dotenv()

ALGOLIA_APP_ID = os.getenv('ALGOLIA_APP_ID')
ALGOLIA_ADMIN_API_KEY = os.getenv('ALGOLIA_ADMIN_API_KEY')
ALGOLIA_INDEX_NAME = os.getenv('ALGOLIA_INDEX_NAME')

client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_ADMIN_API_KEY)
index = client.init_index(ALGOLIA_INDEX_NAME)


def search_text(text):
    res = index.search(text)
    name = {}
    i = 0
    # store all result into a dict and use as return
    for r in res['hits']: 
        name[i] = r['_highlightResult']['data']['name']['value'].replace('<em>' , '').replace('</em>' , '')
        i = i+1
    print(name)
    return name

if __name__ == '__main__':
    search_text('foundation')
