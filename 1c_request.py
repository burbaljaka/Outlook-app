import requests
import json

link_to_site = 'https://community-open-weather-map.p.rapidapi.com/weather'

headers={
    "X-RapidAPI-Host": "community-open-weather-map.p.rapidapi.com",
    "X-RapidAPI-Key": "5aabc22e25msh45d6df4abdd28d0p1a4479jsn10ea7369318e"
        }

parameters = {
            'q':'Ryazan,ru',
            'units':'metric',


}



r = requests.get(link_to_site, headers=headers, params=parameters)
weather = r.json()
print(weather['main']['temp'])
