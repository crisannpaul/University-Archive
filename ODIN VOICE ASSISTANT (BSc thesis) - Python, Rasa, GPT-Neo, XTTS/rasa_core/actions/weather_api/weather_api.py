import os
import requests
from datetime import datetime, timedelta

API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY', '')


def fetch_weather(location):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': location,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    if response.ok:
        return response.json()
    else:
        response.raise_for_status()


def fetch_forecast(location, input_datetime):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': location,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    if response.ok:
        forecast_data = response.json()
        closest_forecast = min(
            forecast_data['list'],
            key=lambda x: abs(input_datetime - datetime.strptime(x['dt_txt'], '%Y-%m-%d %H:%M:%S'))
        )
        return closest_forecast
    else:
        response.raise_for_status()


if __name__ == "__main__":
    print(fetch_forecast('Cluj-Napoca', datetime.now().replace(day=4)))
