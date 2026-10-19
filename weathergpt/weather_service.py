"""Functions for getting live weather data from the free Open-Meteo API.

Open-Meteo does not require an API key for the public endpoints used here.
This module only retrieves and prepares data; it does not make predictions.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import requests


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT_SECONDS = 10


class WeatherServiceError(Exception):
    """Base error for a problem while finding or retrieving weather data."""


class CityNotFoundError(WeatherServiceError):
    """Raised when the city is empty or cannot be found by Open-Meteo."""


# WMO weather interpretation codes returned by Open-Meteo.
WEATHER_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def weather_description(weather_code: int | None) -> str:
    """Convert an API WMO number into a human-readable weather description."""
    return WEATHER_DESCRIPTIONS.get(weather_code, "Weather condition unavailable")


def find_city(city_name: str) -> dict[str, Any]:
    """Find the latitude and longitude for a city typed by the user.

    The forecast endpoint needs coordinates, so this function first asks the
    Open-Meteo geocoding endpoint to convert a city name into coordinates.
    """
    cleaned_city = city_name.strip()
    if not cleaned_city:
        raise CityNotFoundError("Please enter a city name before loading weather.")

    try:
        response = requests.get(
            GEOCODING_URL,
            params={"name": cleaned_city, "count": 1, "language": "en", "format": "json"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as error:
        raise WeatherServiceError(
            "Could not contact the city search service. Check your internet connection and try again."
        ) from error

    results = payload.get("results", [])
    if not results:
        raise CityNotFoundError(
            f"I could not find '{cleaned_city}'. Check the spelling or try a larger nearby city."
        )
    return results[0]


def get_weather_for_city(city_name: str) -> dict[str, Any]:
    """Get current conditions and a short daily forecast for one city.

    The returned dictionary is used by the user interface and the rule-based
    chatbot. Values are live API observations/forecasts, not hardcoded values.
    """
    location = find_city(city_name)
    parameters = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "precipitation,rain,weather_code,wind_speed_10m"
        ),
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 4,
    }

    try:
        response = requests.get(FORECAST_URL, params=parameters, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        api_data = response.json()
    except (requests.RequestException, ValueError) as error:
        raise WeatherServiceError(
            "Weather data is temporarily unavailable. Check your internet connection and try again."
        ) from error

    if not api_data.get("current") or not api_data.get("daily"):
        raise WeatherServiceError("The weather service returned incomplete data. Please try again shortly.")

    return {
        "location": location,
        "current": api_data["current"],
        "daily": api_data["daily"],
        "timezone": api_data.get("timezone", "local time"),
    }


def location_label(weather_data: dict[str, Any]) -> str:
    """Build a clean location label such as 'Phagwara, Punjab, India'."""
    location = weather_data["location"]
    parts = [location.get("name"), location.get("admin1"), location.get("country")]
    unique_parts: list[str] = []
    for part in parts:
        if part and part not in unique_parts:
            unique_parts.append(part)
    return ", ".join(unique_parts)


def today_rain_probability(weather_data: dict[str, Any]) -> int | None:
    """Return today's maximum rain probability from the daily API forecast."""
    probabilities = weather_data["daily"].get("precipitation_probability_max", [])
    return probabilities[0] if probabilities else None


def forecast_rows(weather_data: dict[str, Any], number_of_days: int = 3) -> list[dict[str, str]]:
    """Turn parallel daily API lists into rows that Streamlit can display."""
    daily = weather_data["daily"]
    rows: list[dict[str, str]] = []
    dates = daily.get("time", [])[:number_of_days]

    for index, date_text in enumerate(dates):
        try:
            day_name = datetime.strptime(date_text, "%Y-%m-%d").strftime("%a, %d %b")
        except ValueError:
            day_name = date_text

        max_temperatures = daily.get("temperature_2m_max", [])
        min_temperatures = daily.get("temperature_2m_min", [])
        codes = daily.get("weather_code", [])
        rain_probabilities = daily.get("precipitation_probability_max", [])

        maximum = max_temperatures[index] if index < len(max_temperatures) else None
        minimum = min_temperatures[index] if index < len(min_temperatures) else None
        code = codes[index] if index < len(codes) else None
        rain_probability = rain_probabilities[index] if index < len(rain_probabilities) else None

        rows.append(
            {
                "Date": day_name,
                "Condition": weather_description(code),
                "Min / Max": f"{minimum}°C / {maximum}°C",
                "Rain chance": f"{rain_probability}%" if rain_probability is not None else "Not available",
            }
        )
    return rows


def short_forecast_text(weather_data: dict[str, Any]) -> str:
    """Create a short, readable forecast sentence using only API results."""
    rows = forecast_rows(weather_data)
    if not rows:
        return "A short forecast is not available right now."

    sentences = [
        f"{row['Date']}: {row['Condition']}, {row['Min / Max']}, rain chance {row['Rain chance']}"
        for row in rows
    ]
    return "Short forecast from Open-Meteo — " + "; ".join(sentences) + "."
