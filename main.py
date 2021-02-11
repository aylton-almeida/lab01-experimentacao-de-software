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

# Api query
query = """query example {
  search(query: "stars:>100", type:REPOSITORY, first:100) {
    nodes {
      ... on Repository {
        name
      }
    }
  }
}"""

# Make request
response: Response = requests.post(url, json={'query': query}, headers={
    'Authorization': token
})

if response.status_code != 200 or 'errors' in response.text:
    raise Exception('There was an error while trying to make the request')

data: dict = json.loads(response.text)

data_frame = pd.DataFrame(data['data']['search']['nodes'])

with open('data.csv', 'w') as file:
    data_frame.to_csv(file)


pprint(data_frame)
