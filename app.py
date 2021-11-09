from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from bs4 import BeautifulSoup
import requests
import os

app = Flask(__name__)
Bootstrap(app)

def get_distance(startingcity, destinationcity):
    url = f'https://www.distance24.org/route.json?stops={startingcity}|{destinationcity}'
    response = requests.get(url).json()
    return response["distance"]

def get_source(airplane):
    # must assign airplane.replace to variable, otherwise changed string will not be stored
    airplane = airplane.replace(" ", "-")
    url = f'https://www.airlines-inform.com/commercial-aircraft/{airplane}.html'
    return url

def get_soup(airplane):
    url = get_source(airplane)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def get_picture(soup, i):
    picture = soup.find(class_="setWOfMe")
    src = picture['src']
    r = requests.get(src)
    img_name = "img" + str(i) + ".jpg"
    # MUST place images in static folder. Don't use /static. Use "static" to prevent absolute/relative path issue
    with open("static/images/" + img_name, 'wb') as f:
        f.write(r.content)
    return src

def get_range(range):
    if len(range) > 5:
        range = range[-5:]
    range = int(range)
    return range

def get_seats(soup):
    string = soup.find("td", text="Passengers (2-class)")
    if string is None:
        string = soup.find("td", text="Passengers (1-class)")
    if string is None:
        string = soup.find("td", text="Passengers (3-class)")
    next_string = string.find_next("td")
    seats = next_string.text.strip()
    # retain large end of returned string and convert to int
    seats = int(seats[-3:])
    return seats

def get_efficiency(fuel, range, seats):
    #string = soup.find("td", text="Max stock of fuel (kg)")
    #if string is None: # is already in liters
        #string = soup.find("td", text="Standard fuel capacity (litres)")
        #next_string = string.find_next("td")
        #max_fuel = next_string.text.strip()
        # remove spaces

    fuel = fuel[-6:]
    if fuel[0] == "-":
        fuel = fuel[1:]
    # convert to int
    fuel = int(fuel)
    range = int(range)
    seats = int(seats[-3:])
    fuel_density = 0.807 # kg per liter
    # obtain max fuel in liters rounded to 3 decimals
    fuel_kg = fuel/fuel_density
    # obtain liter/(seat-km) for fuel efficiency
    efficiency = fuel_kg/(seats*range)
    efficiency = round(efficiency, 5)
    # round to 3 places
    return efficiency

def range_check(airplanes, distance):
    new_dict = {}
    for key, value in airplanes.items():
        if int(value["range"]) > distance:
            new_dict[key] = value
    return new_dict

def priority_sort(airplanes, priority):
    #sort the priority
    priorities = []
    for key, value in airplanes.items():
        priorities.append(value[priority])
    if priority == "efficiency":
        priorities = sorted(priorities)
    else:
        priorities = sorted(priorities, reverse=True)
    # create new dictionary
    sorted_dict = {}
    counter = 0
    for i in priorities:
        for key, value in airplanes.items():
            if value[priority] == i:
                sorted_dict[counter] = value
                counter += 1
    
    return sorted_dict

def compress(airplanes):
    counter = 0
    new_dict = {}
    for key, value in airplanes.items():
        new_dict[counter] = value
        counter += 1
    return new_dict

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset', methods=['GET'])
def reset():
    return render_template('index.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    startingcity = request.form['starting-city']
    destinationcity = request.form['destination-city']
    distance = get_distance(startingcity, destinationcity)
    priority = request.form['gridRadios']
    airplane_names = {"name" : ["Airbus A320neo", "Airbus A321neo", "Airbus A330-300", "Airbus A340-600", "Airbus A350-1000",
                    "Airbus A380", "Boeing 737 MAX 7", "Boeing 737 MAX 8", "Boeing 737 MAX 10", "Boeing 767-300", "Boeing 777-9", 
                    "Boeing 787-10"]}
    # 'bombardier-cs100', 'bombardier-cs300', 
    # build dictionary of dictionaries using scraper
    
    # microservice URL
    url = 'http://flip3.engr.oregonstate.edu:8776'
    response = requests.post(url=url, json=airplane_names)
    # convert to json
    response = response.json()

    airplane_details = response
    
    for i in airplane_details:
        # Create dictionary or will get keyerror0
        #soup = get_soup(airplane_details[i]["name"])
        airplane_details[i]["range"] = get_range(airplane_details[i]["range"])
        airplane_details[i]["efficiency"] = get_efficiency(airplane_details[i]["fuel"], airplane_details[i]["range"], airplane_details[i]["seats"])
        airplane_details[i]["source"] = get_source(airplane_details[i]["name"])

    #check range
    airplane_details = range_check(airplane_details, distance)
    #sort by priority
    airplane_details = priority_sort(airplane_details, priority)
    #include pictures
    # will iterate up to (last number-1)
    for i in range(0, 3):
        soup = get_soup(airplane_details[i]["name"])
        airplane_details[i]["picture"] = get_picture(soup, i)

    return render_template('result.html', distance=distance, startingcity=startingcity, 
    destinationcity=destinationcity, priority=priority, airplane_details=airplane_details)

if __name__ == '__main__' :
    port = int(os.environ.get('PORT', 4517))
    app.run(port=port, debug=True)