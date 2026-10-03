import unittest
from unittest.mock import patch
import requests
from datetime import datetime
from weather_api import fetch_weather, fetch_forecast, API_KEY


class TestWeatherAPI(unittest.TestCase):

    @patch('weather_api.requests.get')
    def test_fetch_weather_success(self, mock_get):
        mock_response = {
            'weather': [{'description': 'clear sky'}],
            'main': {'temp': 25.0},
            'name': 'Cluj-Napoca'
        }
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = mock_response

        result = fetch_weather('Cluj-Napoca')
        self.assertEqual(result, mock_response)
        mock_get.assert_called_once_with(
            'http://api.openweathermap.org/data/2.5/weather',
            params={'q': 'Cluj-Napoca', 'appid': API_KEY, 'units': 'metric'}
        )

    @patch('weather_api.requests.get')
    def test_fetch_weather_failure(self, mock_get):
        mock_get.return_value.ok = False
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError

        with self.assertRaises(requests.exceptions.HTTPError):
            fetch_weather('InvalidCity')
        mock_get.assert_called_once_with(
            'http://api.openweathermap.org/data/2.5/weather',
            params={'q': 'InvalidCity', 'appid': API_KEY, 'units': 'metric'}
        )

    @patch('weather_api.requests.get')
    def test_fetch_forecast_success(self, mock_get):
        mock_response = {
            'list': [
                {'dt_txt': '2024-07-08 12:00:00', 'main': {'temp': 30.6}},
                {'dt_txt': '2024-07-08 15:00:00', 'main': {'temp': 32.0}}
            ]
        }
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = mock_response

        input_datetime = datetime.strptime('2024-07-08 13:00:00', '%Y-%m-%d %H:%M:%S')
        result = fetch_forecast('Cluj-Napoca', input_datetime)
        expected = {'dt_txt': '2024-07-08 12:00:00', 'main': {'temp': 30.6}}

        self.assertEqual(result, expected)
        mock_get.assert_called_once_with(
            'http://api.openweathermap.org/data/2.5/forecast',
            params={'q': 'Cluj-Napoca', 'appid': API_KEY, 'units': 'metric'}
        )

    @patch('weather_api.requests.get')
    def test_fetch_forecast_failure(self, mock_get):
        mock_get.return_value.ok = False
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError

        input_datetime = datetime.strptime('2024-07-08 13:00:00', '%Y-%m-%d %H:%M:%S')
        with self.assertRaises(requests.exceptions.HTTPError):
            fetch_forecast('InvalidCity', input_datetime)
        mock_get.assert_called_once_with(
            'http://api.openweathermap.org/data/2.5/forecast',
            params={'q': 'InvalidCity', 'appid': API_KEY, 'units': 'metric'}
        )


if __name__ == '__main__':
    unittest.main()
