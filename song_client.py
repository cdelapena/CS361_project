import requests
import json

url = 'http://localhost:4517/'
# Request: {'num_tracks':[number of tracks], 'date': [date that corresponds w/ sunday of any given week]}
# Response: {'artist_1' : 'song_1', 'artist_2':'song_2' ...}
query = {'num_tracks' : 3, 'date' : '2018-06-01'}
json_dump = json.dumps(query)
print(json_dump)
response = requests.post(url=url, json=json_dump)

data = response.json()
print(data)