# WeatherGPT — 5-Minute Classroom Presentation Script

Use this as a guide, not something you must memorise word-for-word. The timings are approximate. During the live demo, wait for real API data rather than saying a fixed temperature.

## 0:00–0:30 — Introduction

“Good morning everyone. My project is called **WeatherGPT: Conversational AI for Weather Forecasting, Alerts, and Climate Information**. It is a simple Python web application that lets a user select a city and ask basic questions about its weather in a chat-style interface.

The important point is that WeatherGPT is not a trained ChatGPT-like model. It retrieves real current weather and forecast data from the Open-Meteo API, and then uses simple rule-based Python logic to answer questions.”

## 0:30–1:05 — Problem and objective

“People often want simple answers such as: What is the temperature? Will it rain tomorrow? Are there weather alerts? A normal weather website can show many numbers, but beginners may find them difficult to read quickly.

My objective was to make a small conversational interface that converts selected weather data into clear English answers. I also wanted the project to be simple enough to understand, explain, and test as a second-year AI and ML student.”

## 1:05–1:45 — Technology and architecture

“I used Python as the main language and Streamlit to make the web interface. Streamlit lets us create a webpage using Python code, without needing to write HTML or JavaScript.

For live weather data I used Open-Meteo. It has a public endpoint, so this version does not need an API key or paid service.

The project has four main code parts. `weather_service.py` finds city coordinates and gets weather data. `chatbot.py` identifies question intent and makes answer text. `alerts.py` applies fixed thresholds. Finally, `app.py` creates the Streamlit screen and connects everything.”

## 1:45–2:35 — Explain the two algorithms

“The first algorithm is a rule-based intent detector. When a user asks a question, the program changes it to lower case and checks for keywords using `if` and `elif` statements. For example, words such as temperature or temp select the temperature answer. Humidity selects the humidity answer. Forecast or tomorrow selects the forecast answer.

The order of the rules matters. For example, ‘Will it rain tomorrow?’ contains both rain and tomorrow. I check forecast before rain, so the app gives the forecast rather than only today’s rain chance.

The second algorithm is the threshold-based alert system. If current temperature is at least 40 degrees Celsius, it creates a heat alert. If it is at most 5 degrees, it creates a cold alert. If the API’s daily rain probability is at least 70 percent, it creates a rain alert. These are teaching thresholds, not official weather warnings.”

## 2:35–3:45 — Live demo

“Now I will demonstrate the application. In the sidebar I enter a city, for example Phagwara, and click Load live weather. First, the program calls a geocoding API to convert the city name into latitude and longitude. Then it sends those coordinates to the forecast API.

[Load the city. Point to the live cards.]

Here the interface displays the values returned by the API: current temperature, humidity, today’s forecast rain chance, and weather condition. Below that it displays any threshold alert and a short forecast table.

[Ask a question such as ‘What is the temperature?’]

The app identifies this as a temperature intent and inserts the current API value into an answer sentence.

[Ask ‘Will it rain tomorrow?’]

This question becomes a forecast intent because of the word tomorrow. The answer uses the forecast values supplied by Open-Meteo. The app does not claim that it predicted the future by itself.

[Ask ‘What is climate?’]

It also has a small educational section: weather is short-term atmospheric conditions, while climate is the long-term pattern of weather over many years.”

## 3:45–4:25 — Error handling and testing

“I added error handling because a real app should not crash when something goes wrong. If a city is not found, the user gets a spelling or nearby-city suggestion. If the internet or API is unavailable, the user gets a clear retry message. If a question is not supported, the chatbot states the types of questions it can answer instead of inventing an answer.

I also wrote offline unit tests for the keyword priority, alert thresholds, answer templates, and forecast rows. These tests use sample data only to verify the logic. The live application itself retrieves its values from the API.”

## 4:25–5:00 — Limitations and conclusion

“The main limitation is that keyword matching understands only a small number of English question styles. The app also depends on the weather API and its forecast accuracy. The alert thresholds are simple demonstration values, not official public-safety alerts.

In a future version, I could add more languages, saved history, location-aware thresholds, charts, and a properly trained intent classifier with labelled data. In conclusion, WeatherGPT demonstrates how APIs, a rule-based conversational system, and simple decision rules can create a useful beginner AI and ML project. Thank you.”

## Helpful live-demo checklist

Before presenting:

- Start the app with `streamlit run app.py`.
- Confirm your internet connection works and load a city once.
- Do not promise any specific temperature, rain chance, or alert; these are live API results and will change.
- Keep one backup screenshot or use the code explanation if the internet becomes unavailable.
- Be ready to say, “The project retrieves forecast values supplied by Open-Meteo; it does not independently predict weather.”
