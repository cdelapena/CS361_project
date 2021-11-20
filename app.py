from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from bs4 import BeautifulSoup
import requests
import os

app = Flask(__name__)
Bootstrap(app)

# Establish set of airplanes to include in comparison
airplane_names = {"name" : ["Airbus A320neo", "Airbus A321neo", "Airbus A330-300", "Airbus A340-600", "Airbus A350-1000",
                    "Airbus A380", "Boeing 737 MAX 7", "Boeing 737 MAX 8", "Boeing 737 MAX 10", "Boeing 767-300", "Boeing 777-9", 
                    "Boeing 787-10"]}

def get_distance(startingcity, destinationcity):
    """
    Utilize API to return kilometers between 2 cities
    """
    url = f'https://www.distance24.org/route.json?stops={startingcity}|{destinationcity}'
    response = requests.get(url).json()
    return response["distance"]

def populate_details(airplane_details, distance, priority):
    """
    Modify and populate JSON object returned from microservice with additional information.
    """
    for i in airplane_details:
        airplane_details[i]["range"] = get_range(airplane_details[i]["range"])
        airplane_details[i]["efficiency"] = get_efficiency(airplane_details[i]["fuel"], airplane_details[i]["range"], airplane_details[i]["seats"])
        airplane_details[i]["source"] = get_source(airplane_details[i]["name"])

    airplane_details = range_check(airplane_details, distance)
    airplane_details = priority_sort(airplane_details, priority)
    airplane_details = get_picture(airplane_details)
    
    return airplane_details

def get_range(range):
    """
    Converts string returned by microservice to integer.
    """
    # Strip away characters that exceed 5 figures. No commercial airplanes have a 6 figure range.
    if len(range) > 5:
        range = range[-5:]
    range = int(range)
    return range

def get_efficiency(fuel, range, seats):
    """
    Calculate flight efficiency in terms of liters/(seat-km)
    """
    # Strip away characters exceeding 6 characters, as no commercial airplane carries millions of liters of fuel. 
    fuel = fuel[-6:]
    if fuel[0] == "-":
        fuel = fuel[1:]
    # Convert strings to int
    fuel = int(fuel)
    seats = int(seats[-3:])
    fuel_density = 0.807 # kg per liter
    fuel_kg = fuel/fuel_density
    efficiency = fuel_kg/(seats*range)
    efficiency = round(efficiency, 3)
    return efficiency

def get_source(airplane):
    """
    Obtain source URL for airplane data. Replace spaces with dashes to build correct URL
    """
    airplane = airplane.replace(" ", "-")
    url = f'https://www.airlines-inform.com/commercial-aircraft/{airplane}.html'
    return url

def range_check(airplanes, distance):
    """
    Returns a new dictionary from original airplane list where airplanes that cannot meet the range between starting and end cities are removed
    """
    new_dict = {}
    for key, value in airplanes.items():
        if int(value["range"]) > distance:
            new_dict[key] = value
    return new_dict

def priority_sort(airplanes, priority):
    """
    Sort airplanes in descending optimal order
    """
    # Create list from airplane_details dictionary. Only list can be sorted. Dictionary cannot be sorted.
    priorities = []
    for key, value in airplanes.items():
        priorities.append(value[priority])
    if priority == "efficiency":
        priorities = sorted(priorities)
    else:
        priorities = sorted(priorities, reverse=True)
    # Create dictionary from list of priorities in descending optimal order
    sorted_dict = {}
    counter = 0
    for i in priorities:
        for key, value in airplanes.items():
            if value[priority] == i:
                sorted_dict[counter] = value
                counter += 1
    return sorted_dict

def get_soup(airplane):
    """
    Use Beautiful Soup to get raw html for scraping.
    """
    url = get_source(airplane)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def get_picture(airplane_details):
    """
    Obtain pictures of top 3 airplanes.
    """
    for i in range(0, 3):
        soup = get_soup(airplane_details[i]["name"]) 
        picture = soup.find(class_="setWOfMe")
        src = picture['src']
        r = requests.get(src)
        img_name = "img" + str(i) + ".jpg"
        # MUST place images in static folder. Don't use /static. Use "static" to prevent absolute/relative path issue
        with open("static/images/" + img_name, 'wb') as f:
            f.write(r.content)
    return airplane_details

@app.route('/')
def index():
    """
    Displays home page
    """
    return render_template('index.html')

@app.route('/reset', methods=['GET'])
def reset():
    """
    Returns to home page
    """
    return render_template('index.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    """
    Utilize microservice to obtain top performing airplanes dependant on selected criteria.
    """

    # Determine distance between cities to establish minimum range
    startingcity = request.form['starting-city']
    destinationcity = request.form['destination-city']
    distance = get_distance(startingcity, destinationcity)

    # Determine priority
    priority = request.form['gridRadios']
    
    # call microservice and store response
    url = 'http://flip3.engr.oregonstate.edu:8776'
    response = requests.post(url=url, json=airplane_names)

    # microservice data is returned as a string. Convert to JSON
    response = response.json()

    # microservice response contains {name: {range(str), seats(str), fuel(str, in liters)}}.
    airplane_details = response
    airplane_details = populate_details(airplane_details, distance, priority)

    return render_template('result.html', distance=distance, startingcity=startingcity, 
    destinationcity=destinationcity, priority=priority, airplane_details=airplane_details)

if __name__ == '__main__' :
    port = int(os.environ.get('PORT', 4521))
    app.run(port=port, debug=True)