"""Offline tests for the rule-based parts of WeatherGPT.

These tests use made-up data only to check the code logic. The app itself
never displays hardcoded weather values; it gets its displayed data from the API.
"""

import unittest
from unittest.mock import patch

import requests

from alerts import create_alerts
from chatbot import answer_question, detect_intent
from weather_service import CityNotFoundError, WeatherServiceError, find_city, forecast_rows


SAMPLE_WEATHER_DATA = {
    "location": {"name": "Test City", "admin1": "Test State", "country": "Test Country"},
    "current": {
        "temperature_2m": 42.0,
        "relative_humidity_2m": 60,
        "apparent_temperature": 44.0,
        "rain": 0.0,
        "weather_code": 1,
        "wind_speed_10m": 12.0,
    },
    "daily": {
        "time": ["2026-10-19", "2026-10-20", "2026-10-21"],
        "weather_code": [1, 61, 3],
        "temperature_2m_max": [42.0, 32.0, 30.0],
        "temperature_2m_min": [28.0, 24.0, 22.0],
        "precipitation_probability_max": [80, 85, 15],
    },
    "timezone": "Asia/Kolkata",
}


class IntentTests(unittest.TestCase):
    """Check that keyword rules pick the expected question category."""

    def test_forecast_has_priority_over_rain(self):
        self.assertEqual(detect_intent("Will it rain tomorrow?"), "forecast")

    def test_temperature_question(self):
        self.assertEqual(detect_intent("What is the current temperature?"), "temperature")

    def test_unsupported_question(self):
        self.assertEqual(detect_intent("Tell me a joke"), "unsupported")


class AlertTests(unittest.TestCase):
    """Check the high-temperature and rain-probability thresholds."""

    def test_heat_and_rain_alerts_are_created(self):
        alerts = create_alerts(SAMPLE_WEATHER_DATA)
        messages = " ".join(alert["message"] for alert in alerts)
        self.assertIn("Heat alert", messages)
        self.assertIn("Rain alert", messages)

    def test_no_alerts_when_values_are_safe(self):
        safe_data = {
            **SAMPLE_WEATHER_DATA,
            "current": {**SAMPLE_WEATHER_DATA["current"], "temperature_2m": 25.0},
            "daily": {
                **SAMPLE_WEATHER_DATA["daily"],
                "precipitation_probability_max": [20, 30, 10],
            },
        }
        self.assertEqual(create_alerts(safe_data), [])


class AnswerAndForecastTests(unittest.TestCase):
    """Check that response text and table rows are made from supplied data."""

    def test_temperature_answer_uses_current_value(self):
        response = answer_question("What is the temperature?", SAMPLE_WEATHER_DATA, [])
        self.assertIn("42.0°C", response)

    def test_three_forecast_rows_are_created(self):
        rows = forecast_rows(SAMPLE_WEATHER_DATA)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1]["Condition"], "Slight rain")


class ErrorHandlingTests(unittest.TestCase):
    """Check friendly errors without making a real internet request."""

    def test_empty_city_raises_city_not_found_error(self):
        with self.assertRaises(CityNotFoundError):
            find_city("   ")

    @patch("weather_service.requests.get")
    def test_network_error_becomes_weather_service_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("Offline for test")
        with self.assertRaises(WeatherServiceError):
            find_city("Phagwara")


if __name__ == "__main__":
    unittest.main()
