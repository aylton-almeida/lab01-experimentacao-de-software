import requests
import json
import pandas as pd
import os
import progressbar

from pprint import pprint
from dotenv import load_dotenv
from requests.models import Response

# Load env file
load_dotenv()

# Get env variables
url = os.getenv('API_URL')
token = 'Bearer {}'.format(os.getenv('AUTH_TOKEN'))


def getQuery(cursor: str = None):
    ###
    # build api query
    # ###
    return """
    query example{
      search(type: REPOSITORY, first: 100, query: "stars:>100", after: %s) {
        edges {
            cursor
            node {
              ... on Repository {
                name
                createdAt
                primaryLanguage {
                  name
                }
                issues {
                  totalCount
                }
                pullRequests {
                  totalCount
                }
                pushedAt
                updatedAt
                releases {
                  totalCount
                }
              }
            }
        }
      }
    }
    """ % (cursor or 'null')


repo_list: list = []

# extremely necessary progress bar for better user experience
widgets = [
    '\x1b[33mFetching repos...\x1b[39m',
    progressbar.Percentage(),
    progressbar.Bar(marker='\x1b[32m#\x1b[39m'),
]
bar = progressbar.ProgressBar(
    widgets=widgets, max_value=10, min_value=0).start()

for i in range(10):
    # Make 1000 requests

    current_cursor = '"{}"'.format(repo_list[-1]['cursor']) if len(
        repo_list) > 0 else None

    query = getQuery(current_cursor)

    response: Response = requests.post(url, json={'query': query}, headers={
        'Authorization': token
    })

    if response.status_code != 200 or 'errors' in response.text:
        print(response.text)
        raise Exception('There was an error while trying to make the request')

    json_data: dict = json.loads(response.text)

    repo_data = json_data['data']['search']['edges']

    repo_list = [*repo_list, *repo_data]
    bar.update(i + 1)

bar.finish()

print('All repos were fetch')
print('Saving file...')


data_frame = pd.DataFrame(list(map(lambda item: {
    "name": item.get('node').get('name'),
    "created_at": item.get('node').get("createdAt"),
    "primary_language": item.get('node').get('primaryLanguage').get('name') if item.get('node').get('primaryLanguage') else None,
    "issues": item.get('node').get('issues').get('totalCount') if item.get('node').get('issues') else None,
    "pull_requests": item.get('node').get('pullRequests').get('totalCount') if item.get('node').get('pullRequests') else None,
    "pushed_at": item.get('node').get('pushedAt'),
    "updated_at": item.get('node').get('updatedAt'),
    "releases": item.get('node').get('releases').get('totalCount') if item.get('node').get('releases') else None
}, repo_list)))

with open('data.csv', 'w') as file:
    data_frame.to_csv(file)

print('File saved')
