"""Streamlit user interface for the WeatherGPT college project."""

from __future__ import annotations

from typing import Any

import streamlit as st

from alerts import create_alerts
from chatbot import CLIMATE_EXPLANATION, answer_question
from weather_service import (
    CityNotFoundError,
    WeatherServiceError,
    forecast_rows,
    get_weather_for_city,
    location_label,
    today_rain_probability,
    weather_description,
)


st.set_page_config(page_title="WeatherGPT", page_icon="🌦️", layout="wide")


def initialise_session_state() -> None:
    """Create variables that Streamlit should remember between page reruns."""
    if "weather_data" not in st.session_state:
        st.session_state["weather_data"] = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "question_history" not in st.session_state:
        st.session_state.question_history = []


def load_weather(city_name: str) -> None:
    """Fetch a city's data and store it, while showing friendly errors."""
    try:
        with st.spinner("Getting live weather data from Open-Meteo..."):
            st.session_state.weather_data = get_weather_for_city(city_name)
        st.session_state.messages = []
        st.success(f"Live data loaded for {location_label(st.session_state.weather_data)}.")
    except CityNotFoundError as error:
        st.error(str(error))
    except WeatherServiceError as error:
        st.error(str(error))


def show_weather_dashboard(weather_data: dict[str, Any]) -> list[dict[str, str]]:
    """Show the current measurements, simple alert cards, and forecast table."""
    current = weather_data["current"]
    city = location_label(weather_data)
    rain_probability = today_rain_probability(weather_data)
    alerts = create_alerts(weather_data)

    st.subheader(f"Live weather: {city}")
    st.caption(
        f"Current values supplied by Open-Meteo. Timezone returned by API: {weather_data['timezone']}."
    )

    temperature_column, humidity_column, rain_column, condition_column = st.columns(4)
    temperature_column.metric("Temperature", f"{current.get('temperature_2m')} °C")
    humidity_column.metric("Humidity", f"{current.get('relative_humidity_2m')} %")
    rain_column.metric(
        "Today's rain chance",
        f"{rain_probability} %" if rain_probability is not None else "Not available",
    )
    condition_column.metric("Condition", weather_description(current.get("weather_code")))

    st.subheader("Threshold-based alerts")
    if alerts:
        for alert in alerts:
            if alert["level"] == "High":
                st.warning(alert["message"])
            else:
                st.info(alert["message"])
    else:
        st.success("No teaching-threshold alerts are active for the currently loaded data.")
    st.caption("These are project thresholds, not official government weather warnings.")

    st.subheader("Short forecast")
    st.dataframe(forecast_rows(weather_data), hide_index=True, use_container_width=True)
    st.caption("Forecast values come from Open-Meteo and can change when the API updates them.")
    return alerts


def show_chat(weather_data: dict[str, Any], alerts: list[dict[str, str]]) -> None:
    """Render previous messages and respond to one new chat question."""
    st.subheader("Ask WeatherGPT")
    st.caption(
        "Try: “What is the temperature?”, “Will it rain tomorrow?”, “Show alerts”, or “What is climate?”"
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input("Ask a weather question for the loaded city")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.question_history.insert(0, question)
        st.session_state.question_history = st.session_state.question_history[:8]

        with st.chat_message("user"):
            st.write(question)

        answer = answer_question(question, weather_data, alerts)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.write(answer)


def main() -> None:
    """Arrange the Streamlit page and call the smaller UI functions."""
    initialise_session_state()

    st.title("🌦️ WeatherGPT")
    st.write("A beginner-friendly, rule-based weather chatbot for a college AI & ML project.")
    st.info(
        "Honest project note: WeatherGPT retrieves data from Open-Meteo and answers using "
        "keyword rules. It is not a trained generative AI model and does not create its own forecast."
    )

    with st.sidebar:
        st.header("Choose a city")
        city_name = st.text_input("City name", placeholder="Example: Phagwara")
        if st.button("Load live weather", type="primary", use_container_width=True):
            load_weather(city_name)

        st.divider()
        st.subheader("Recent questions")
        if st.session_state.question_history:
            for number, saved_question in enumerate(st.session_state.question_history, start=1):
                st.write(f"{number}. {saved_question}")
        else:
            st.caption("Your latest eight questions will appear here.")

    weather_data = st.session_state.weather_data
    if weather_data is None:
        st.subheader("Start here")
        st.write("Enter a city in the left panel and select **Load live weather**.")
        st.write("The app will first find the city coordinates and then request current weather and a forecast.")
    else:
        alerts = show_weather_dashboard(weather_data)
        show_chat(weather_data, alerts)

    with st.expander("Weather vs climate — classroom note"):
        st.write(CLIMATE_EXPLANATION)

    st.divider()
    st.caption("Data source: Open-Meteo public weather API. No API key is used in this student project.")


if __name__ == "__main__":
    main()
