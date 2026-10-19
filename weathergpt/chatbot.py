"""A small, transparent rule-based chatbot for WeatherGPT.

This is intentionally not a trained language model. It recognises a small
set of question types by checking lower-case words against keyword lists.
"""

from __future__ import annotations

from typing import Any

from weather_service import (
    location_label,
    short_forecast_text,
    today_rain_probability,
    weather_description,
)


CLIMATE_EXPLANATION = (
    "Weather is the short-term condition of the atmosphere at a place—for example, "
    "today's temperature, rain, wind, or humidity. Climate is the usual pattern of "
    "weather in a region measured over a long period, commonly 30 years or more. "
    "This app shows weather data; it does not calculate climate trends."
)


def detect_intent(question: str) -> str:
    """Classify a question using simple keyword matching and if/elif rules.

    The first matching rule wins. For example, 'Will it rain tomorrow?' has
    both a rain keyword and a forecast keyword, so forecast is checked first.
    """
    text = question.lower().strip()

    if any(word in text for word in ["alert", "warning", "warn", "extreme"]):
        return "alerts"
    elif any(word in text for word in ["climate", "global warming", "climate change"]):
        return "climate"
    elif any(word in text for word in ["forecast", "tomorrow", "next day", "next week"]):
        return "forecast"
    elif any(word in text for word in ["humidity", "humid", "moisture"]):
        return "humidity"
    elif any(word in text for word in ["rain", "raining", "precipitation", "umbrella", "wet"]):
        return "rain"
    elif any(word in text for word in ["temperature", "temp", "hot", "cold", "feels like"]):
        return "temperature"
    elif any(word in text for word in ["weather", "condition", "wind", "today", "now", "current"]):
        return "current_weather"
    else:
        return "unsupported"


def _format_alerts(alerts: list[dict[str, str]]) -> str:
    """Convert alert dictionaries into one sentence for a chat answer."""
    if not alerts:
        return "No threshold alerts are active for the currently loaded data."
    return " ".join(alert["message"] for alert in alerts)


def answer_question(
    question: str, weather_data: dict[str, Any], alerts: list[dict[str, str]]
) -> str:
    """Return an answer using the intent and the already retrieved API data."""
    intent = detect_intent(question)
    current = weather_data["current"]
    city = location_label(weather_data)
    temperature = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    feels_like = current.get("apparent_temperature")
    wind = current.get("wind_speed_10m")
    condition = weather_description(current.get("weather_code"))
    rain_probability = today_rain_probability(weather_data)

    if intent == "alerts":
        return f"Alerts for {city}: {_format_alerts(alerts)}"
    elif intent == "climate":
        return CLIMATE_EXPLANATION
    elif intent == "forecast":
        return f"Forecast for {city}: {short_forecast_text(weather_data)}"
    elif intent == "humidity":
        return f"The current humidity in {city} is {humidity}%."
    elif intent == "rain":
        probability_text = (
            f"{rain_probability}%" if rain_probability is not None else "not available"
        )
        return (
            f"The current recorded rain amount in {city} is {current.get('rain')} mm. "
            f"Today's maximum forecast rain probability is {probability_text}."
        )
    elif intent == "temperature":
        return (
            f"The current temperature in {city} is {temperature}°C. "
            f"It feels like {feels_like}°C."
        )
    elif intent == "current_weather":
        return (
            f"Current weather in {city}: {condition}. Temperature: {temperature}°C, "
            f"humidity: {humidity}%, wind speed: {wind} km/h."
        )
    else:
        return (
            "I can answer questions about current weather, temperature, humidity, rain, "
            "forecast, alerts, or climate. For example, ask: 'Will it rain tomorrow?'"
        )
