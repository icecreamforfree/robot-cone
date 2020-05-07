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
    # res = index.search("color")
    res = index.search(text , {
        'attributesToRetrieve': [
            'brand',
            'name'
        ]
    })

    # return res['name']
    # print(res['hits'][0]['_highlightResult']['data']['name']['value'])
    data = res['hits'][0]['_highlightResult']['data']['name']['value'].replace('<em>','').replace('</em>','')
    print(data)
    return data



if __name__ == '__main__':
    search_text('stick')
