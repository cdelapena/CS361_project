import requests
import json

url = 'http://flip3.engr.oregonstate.edu:8776'

query = {"name" : ["Airbus A320neo", "Airbus A321neo", "Airbus A330-800neo", "Airbus A340-600", "Airbus A350-900",
                    "Airbus A380", "Boeing 737 MAX 7", "Boeing 737 MAX 8", "Boeing 737 MAX 10", "Boeing 737 MAX 10", 
                    "Boeing 767-300", "Boeing 777-9",  "Boeing 787-10"]}


response = requests.post(url=url, json=query)

response = response.json()


for i in response:
    print(response[i]["range"])
#query = {"name" : ['airbus-a320neo', 'airbus-a321neo', 'airbus-a330-300', 'boeing-767-300', 'boeing-777-9', 'boeing-737-max-10']}


#json_dump = json.dumps(query)
#print(json_dump)

#response.raise_for_status()
#print(response.text)
#data = response
#print(data)