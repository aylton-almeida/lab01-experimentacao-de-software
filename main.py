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

total_repos = 1000
repos_per_request = 3


def getQuery(cursor: str = None):
    ###
    # build api query
    # ###
    return """
    query example{
      search(type: REPOSITORY, first: %(repos)i, query: "stars:>101", after: %(after)s) {
        edges {
            cursor
            node {
              ... on Repository {
                nameWithOwner
                url
                createdAt
                primaryLanguage {
                  name
                }
                closedIssues: issues(first: 1, states: CLOSED) {
                  totalCount
                }
                totalIssues: issues {
                  totalCount
                }
                pullRequests(first: 1, states: MERGED) {
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
    """ % {'repos': repos_per_request, "after": (cursor or 'null')}


repo_list: list = []


# extremely necessary progress bar for better user experience
widgets = [
    '\x1b[33mFetching repos...\x1b[39m',
    progressbar.Percentage(),
    progressbar.Bar(marker='\x1b[32m#\x1b[39m'),
]
bar = progressbar.ProgressBar(
    widgets=widgets, max_value=int(total_repos / repos_per_request + 1), min_value=0).start()

i = 0
while i < int(total_repos / repos_per_request + 1):
    # Make 1000 requests

    try:
        current_cursor = '"{}"'.format(repo_list[-1]['cursor']) if len(
            repo_list) > 0 else None

        query = getQuery(current_cursor)

        response: Response = requests.post(url, json={'query': query}, headers={
            'Authorization': token
        })

        if response.status_code != 200 or 'errors' in response.text:
            print(response.text)
            raise Exception(
                'There was an error while trying to make the request')

        json_data: dict = json.loads(response.text)

        repo_data = json_data['data']['search']['edges']

        repo_list = [*repo_list, *repo_data]

        i += 1
        bar.update(i)

    except:
        print('Timeout error')


bar.finish()

print('All repos were fetch')
print('Saving file...')


data_frame = pd.DataFrame(list(map(lambda item: {
    "nameWithOwner": item.get('node').get('nameWithOwner'),
    "url": item.get('node').get('url'),
    "created_at": item.get('node').get("createdAt"),
    "primary_language": item.get('node').get('primaryLanguage').get('name') if item.get('node').get('primaryLanguage') else None,
    "closedIssues": item.get('node').get('closedIssues').get('totalCount') if item.get('node').get('closedIssues') else None,
    "totalIssues": item.get('node').get('totalIssues').get('totalCount') if item.get('node').get('totalIssues') else None,
    "pull_requests": item.get('node').get('pullRequests').get('totalCount') if item.get('node').get('pullRequests') else None,
    "pushed_at": item.get('node').get('pushedAt'),
    "updated_at": item.get('node').get('updatedAt'),
    "releases": item.get('node').get('releases').get('totalCount') if item.get('node').get('releases') else None
}, repo_list)))


with open('data.csv', 'w') as file:
    data_frame.to_csv(file)

print('File saved')
