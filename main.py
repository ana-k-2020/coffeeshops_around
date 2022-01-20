import json
import requests
import folium
import os
from geopy import distance
from flask import Flask


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_distances(cafe):
    return cafe['distance']


def cafes_around():
    with open('index.html') as cafes:
        return cafes.read()


if __name__ == '__main__':
    apikey = os.environ['APIKEY']
    location = input('Где вы находитесь? ')
    coords = fetch_coordinates(apikey, location)

    with open('coffee.json', 'r', encoding='CP1251') as coffeeshops:
        coffeeshops = json.loads(coffeeshops.read())

    coffeeshops_new = []
    for cafe in coffeeshops:
        coffeeshops_new.append({
            'title': cafe['Name'],
            'distance': distance.distance(
                            coords[::-1],
                            cafe['geoData']['coordinates'][::-1]
                        ).km,
            'latitude': cafe['geoData']['coordinates'][1],
            'longitude': cafe['geoData']['coordinates'][0],
        })

    go_to = sorted(coffeeshops_new, key=get_distances)[:5]
    me = folium.Map(location=coords[::-1], zoom_start=13)
    for i in go_to:
        folium.Marker(
            [i['latitude'], i['longitude']],
            popup=i['title'],
        ).add_to(me)
    me.save('index.html')

    app = Flask(__name__)
    app.add_url_rule('/', 'cafes around me', cafes_around)
    app.run('0.0.0.0')
