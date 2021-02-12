import requests
import json
import pandas as pd
import os

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
    return """query example {
       search(query: "stars:>100", type:REPOSITORY, first:100, after: %s) {
          edges {
            cursor
            node {
              ... on Repository {
                name
                createdAt
              }
            }
          }
       }
    }""" % (cursor or 'null')


repo_list: list = []

print('Fetching repos...')

# Make 1000 requests
for i in range(10):

    current_cursor = '"{}"'.format(repo_list[-1]['cursor']) if len(
        repo_list) > 0 else None

    print('{} out of 1000. Current cursor: {}'.format(
        (i + 1) * 100, current_cursor))

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

print('All repos were fetch\n')
print('Saving file...')

data_frame = pd.DataFrame(repo_list)

with open('data.csv', 'w') as file:
    data_frame.to_csv(file)

print('File saved')
