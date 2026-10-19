# WeatherGPT — Likely Viva Questions and Short Answers

## Project basics

### 1. What is WeatherGPT?

It is a Python Streamlit web app that retrieves weather data from Open-Meteo, answers a small set of weather questions using keyword rules, and displays simple threshold-based alerts.

### 2. Is it really GPT or generative AI?

No. The name is a project title. This version is a rule-based conversational application, not a trained generative language model. It does not train, learn, or generate an independent forecast.

### 3. Why did you use Python?

Python has simple syntax, strong library support, and is suitable for web prototypes, API requests, data handling, and AI/ML learning.

### 4. Why did you use Streamlit?

Streamlit lets me build an interactive webpage with Python only. It provides inputs, buttons, metric cards, tables, and chat-style components without writing separate front-end code.

### 5. What is an API?

An Application Programming Interface is a way for two software systems to communicate. This app sends requests to Open-Meteo and receives weather data in JSON format.

### 6. Why do you need a geocoding API before the forecast API?

The user enters a city name, but the forecast API needs latitude and longitude. Geocoding converts the city name into coordinates.

### 7. What data format does the API return?

JSON, which maps naturally to Python dictionaries and lists.

### 8. Does this project use an API key?

No. It uses the public Open-Meteo endpoints selected for this student project. A future deployment should check the provider’s current documentation and usage policy.

## Algorithm questions

### 9. What is intent detection in your project?

It is the step that decides what the user is asking for. `detect_intent()` checks lower-case question text for keyword groups and returns labels such as `temperature`, `rain`, or `forecast`.

### 10. Explain `if`/`elif` in your chatbot.

`if` checks the first condition. `elif` means “else if” and checks the next condition only when the earlier one was false. The first matching keyword group chooses the answer type.

### 11. Why is the order of rules important?

One sentence can contain multiple keywords. “Will it rain tomorrow?” contains `rain` and `tomorrow`. Forecast is checked before rain, so the program gives a forecast answer, which is more useful.

### 12. Is keyword matching machine learning?

No. It is a rule-based technique. A person writes the keyword lists and decision order. Machine learning would require a dataset, training process, model evaluation, and learned parameters.

### 13. What is the time complexity of intent detection?

For this small fixed list of keywords, it is effectively linear in the length of the user’s question. It checks each short keyword list once.

### 14. What is a threshold-based alert?

It is a rule that compares a measurement to a fixed limit. For example, if temperature is at least 40°C, the program produces a heat alert.

### 15. What alert rules did you use?

High temperature: at least 40°C. Low temperature: at most 5°C. Rain: today’s maximum API rain probability at least 70%. They are teaching thresholds, not official warnings.

### 16. Why do temperature rules use `if` and `elif`, but rain uses another `if`?

A current temperature cannot be both extremely high and extremely low, so only one temperature rule should apply. Rain can happen with either temperature condition, so it is checked independently.

### 17. What happens when an unsupported question is asked?

The app returns a friendly message listing the supported topics. It does not guess or produce an unrelated answer.

## Code and data questions

### 18. What is `requests.get()`?

It sends an HTTP GET request to a web address to retrieve data. In this project it retrieves JSON responses from Open-Meteo.

### 19. Why is a timeout used?

A timeout stops the app from waiting forever when the network or API is slow or unavailable. This app uses ten seconds.

### 20. How are network errors handled?

The API code catches `requests.RequestException` and raises a friendly custom error. The Streamlit app catches that error and shows a retry message instead of crashing.

### 21. How are invalid city names handled?

If Open-Meteo geocoding returns no results, `find_city()` raises `CityNotFoundError`. The app tells the user to check spelling or try a nearby larger city.

### 22. What is session state?

Streamlit reruns Python after interactions. Session state is a small storage area that remembers the selected city data, chat messages, and recent questions during the browser session.

### 23. Why do you save `weather_data` rather than call the API for every question?

It makes the app faster, reduces unnecessary requests, and ensures the dashboard and several chat answers use the same recently fetched data for the loaded city.

### 24. What is a WMO weather code?

It is a standard numeric code describing a weather condition. The project maps API codes such as 0 or 61 to readable text such as Clear sky or Slight rain.

### 25. Why are type hints used?

Type hints such as `dict[str, Any]` document what kind of value a function expects or returns. They improve readability and help development tools find mistakes; Python does not enforce them by itself at runtime.

### 26. What are unit tests in this project?

They are small offline checks for individual logic functions. They test keyword priority, thresholds, answer templates, and forecast rows without relying on live internet data.

## Limitations

### 27. What are the main limitations?

It understands only selected English keywords, does not extract cities from every sentence, depends on Open-Meteo data, has session-only history, and has demonstration—not official—alert thresholds.

### 28. Does the app accurately predict future weather?

The app does not make its own prediction. It presents forecast values supplied by Open-Meteo, which can change and have uncertainty.

### 29. Can it send emergency alerts?

No. The alert boxes are classroom demonstrations and are not a public-safety warning system. Official alerts should come from authorised government meteorological agencies.

### 30. How could this be improved?

Possible improvements are multilingual keyword support, persistent database history, charts, localised thresholds, official alert integrations, city extraction, and a trained intent classifier evaluated on labelled questions.

## One strong closing answer

If asked why this counts as an AI & ML project when it has no trained ML model, say:

> “It demonstrates a transparent rule-based AI approach: the system maps language patterns to intents and makes decisions from weather data. I intentionally chose this baseline because I can explain and test every decision. It also gives a clear foundation for a future trained classifier, which would require labelled training data and evaluation.”
