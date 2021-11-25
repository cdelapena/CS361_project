import requests
import json
import random
from flask import Flask, request
from bs4 import BeautifulSoup

app = Flask(__name__)
port = 4519

def scrape(response):
    '''Scrape all artists and songs from Billboard 100 list'''
    # use Beautiful soup to parse html
    soup = BeautifulSoup(response.content, 'html.parser')

    # obtain elements from soup
    songs = soup.find_all(class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only")
    artists = soup.find_all(class_="c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only")
    # strip text to obtain song titles and artists
    song_titles = [song.text.strip() for song in songs]
    artist_list = [artist.text.strip() for artist in artists]

    results = {}
    for i in range(0, len(song_titles)):
        results[song_titles[i]] = artist_list[i]

    return results

def select_random(full_list, num_tracks):
    '''Return random dictionary of num_tracks size generated from full song list'''
    counter = 0
    random_dict = {}

    items = list(full_list.items())
    random.shuffle(items)
    for key, value in items:
        random_dict[key] = value
        counter += 1
        if counter == num_tracks:
            break
    
    return random_dict

@app.route('/', methods=['POST', 'GET'])
def index():
    '''Initiate scraping microservice'''
    if request.method == 'POST':
        request_json = request.get_json()
        print('Here is the json request: ', request_json)

        request_dict = json.loads(request_json)

        date = request_dict['date']
        num_tracks = request_dict['num_tracks']
        url = 'https://www.billboard.com/charts/hot-100/' + date
        response = requests.get(url)
        full_list = scrape(response)

        random_list = select_random(full_list, num_tracks)
    
        return random_list

    else:
        print('Get request received. Please make a POST request.')
        return "Get request received. Please make a POST request."

if __name__ == '__main__' :
    app.run(port=port, debug=True)