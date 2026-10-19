"""Simple threshold-based weather alerts used by WeatherGPT."""

from __future__ import annotations

from typing import Any

from weather_service import today_rain_probability


# These are teaching thresholds. They are not official meteorological warnings.
HIGH_TEMPERATURE_C = 40
LOW_TEMPERATURE_C = 5
HIGH_RAIN_PROBABILITY_PERCENT = 70


def create_alerts(weather_data: dict[str, Any]) -> list[dict[str, str]]:
    """Compare live values with fixed thresholds and return matching alerts.

    This algorithm uses simple comparisons instead of machine learning. A
    threshold is a chosen limit: if a value crosses it, an alert is produced.
    """
    alerts: list[dict[str, str]] = []
    temperature = weather_data["current"].get("temperature_2m")
    rain_probability = today_rain_probability(weather_data)

    if temperature is not None and temperature >= HIGH_TEMPERATURE_C:
        alerts.append(
            {
                "level": "High",
                "message": (
                    f"Heat alert: current temperature is {temperature}°C, which is at or above "
                    f"the {HIGH_TEMPERATURE_C}°C teaching threshold."
                ),
            }
        )
    elif temperature is not None and temperature <= LOW_TEMPERATURE_C:
        alerts.append(
            {
                "level": "High",
                "message": (
                    f"Cold alert: current temperature is {temperature}°C, which is at or below "
                    f"the {LOW_TEMPERATURE_C}°C teaching threshold."
                ),
            }
        )

    if rain_probability is not None and rain_probability >= HIGH_RAIN_PROBABILITY_PERCENT:
        alerts.append(
            {
                "level": "Medium",
                "message": (
                    f"Rain alert: today's maximum forecast rain probability is {rain_probability}%, "
                    f"which is at or above the {HIGH_RAIN_PROBABILITY_PERCENT}% teaching threshold."
                ),
            }
        )

    return alerts
