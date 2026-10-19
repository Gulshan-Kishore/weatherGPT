# WeatherGPT: Beginner’s Function-by-Function Explanation

This document explains the code in plain English. Read it with the corresponding Python file open. The aim is that you can explain both the big idea and the reason for every function in a classroom.

## 1. The main idea in one minute

WeatherGPT has three jobs:

1. **Retrieve data:** ask Open-Meteo for a city’s location, current weather, and short forecast.
2. **Understand a basic question:** recognise a few English keywords such as `temperature`, `rain`, and `forecast`.
3. **Make a clear response:** put the relevant API value into a sentence. For alerts, compare a value with a fixed threshold.

There is no trained neural network, language model, or dataset training step. “AI” here means a small **rule-based expert system**: people define the rules, and the program follows them.

## 2. Overall data journey

```text
User enters "Phagwara"
        ↓
find_city("Phagwara") asks the geocoding API
        ↓
API returns latitude and longitude
        ↓
get_weather_for_city(...) asks the forecast API with those coordinates
        ↓
weather_data dictionary is saved in Streamlit session state
        ↓
User asks "Will it rain tomorrow?"
        ↓
detect_intent(...) returns "forecast"
        ↓
answer_question(...) selects short_forecast_text(...)
        ↓
Text appears in the chat window
```

The app makes the API request when the user selects **Load live weather**, not for every chat question. That makes the flow easier to understand and avoids repeating requests unnecessarily while the selected city remains the same.

## 3. `weather_service.py` — API and data helper functions

This file is deliberately separated from the web page. If the API changes, most changes belong here rather than in the chat interface.

### Imports and constants

- `requests` sends HTTP requests to web APIs.
- `datetime` converts API dates such as `2026-10-19` into friendlier dates such as `Mon, 19 Oct`.
- `Any` is a type hint for a dictionary whose values can be several different Python types.
- `GEOCODING_URL` and `FORECAST_URL` store the two API web addresses once, so the code does not repeat long strings.
- `REQUEST_TIMEOUT_SECONDS = 10` means a request will stop waiting after ten seconds.

### `WeatherServiceError`

```python
class WeatherServiceError(Exception):
```

This creates a named kind of error for a general API or network problem. A custom error helps `app.py` catch weather-service problems without catching unrelated programming errors.

### `CityNotFoundError`

```python
class CityNotFoundError(WeatherServiceError):
```

This is a more specific type of `WeatherServiceError`. It is used when the city field is empty or Open-Meteo returns no matching city. The app can then show a spelling suggestion rather than a general internet message.

### `WEATHER_DESCRIPTIONS`

The API returns a WMO numeric weather code, for example `0` or `61`. A dictionary maps those numbers to readable text such as `Clear sky` or `Slight rain`. This is not a prediction algorithm; it is a lookup table provided so the student app can display useful words.

### `weather_description(weather_code)`

**Purpose:** turn one numeric WMO code into readable text.

1. It receives a weather code, which may be `None` if data is missing.
2. It uses `.get(weather_code, fallback)` on the dictionary.
3. If the code exists, it returns the matching description.
4. If it does not exist, it returns `Weather condition unavailable` rather than raising an error.

This fallback is a simple example of defensive programming: the web app remains usable even if a new or missing code appears.

### `find_city(city_name)`

**Purpose:** convert a human city name into latitude and longitude.

The forecast API needs coordinates, so this must happen first.

1. `city_name.strip()` removes spaces at the beginning and end. `"  Delhi  "` becomes `"Delhi"`.
2. If nothing remains, the function raises `CityNotFoundError` immediately. There is no need to call the internet for an empty name.
3. `requests.get(...)` sends a GET request to the geocoding URL. The `params` dictionary becomes URL query values: name, one desired result, English language, and JSON format.
4. `timeout=10` prevents infinite waiting.
5. `response.raise_for_status()` raises an error for a failed HTTP status such as 404 or 500.
6. `except requests.RequestException` catches connection, timeout, and HTTP errors. The code raises a friendly `WeatherServiceError` instead of exposing technical details to the user.
7. `response.json()` turns the JSON response into a Python dictionary. `.get("results", [])` provides an empty list if the field does not exist.
8. If the list is empty, `CityNotFoundError` explains that the user should check spelling or try a nearby large city.
9. Otherwise, `results[0]` returns the first best match, including fields such as city name, country, latitude, and longitude.

### `get_weather_for_city(city_name)`

**Purpose:** retrieve all live weather data the app needs for a selected city.

1. It calls `find_city(city_name)` and saves the returned city record in `location`.
2. It builds a `parameters` dictionary. The latitude and longitude come from the returned location—there are no hardcoded locations.
3. The `current` value asks for only these current fields: temperature, relative humidity, apparent temperature, precipitation, rain, WMO code, and wind speed.
4. The `daily` value asks for daily weather code, maximum/minimum temperature, and maximum precipitation probability.
5. `timezone="auto"` asks the API to use the selected location’s timezone.
6. `forecast_days=4` requests enough days for a compact three-day display and a small margin if the API response changes.
7. A second `requests.get` calls the forecast endpoint.
8. The `try/except` handles both connection errors and invalid JSON with the same user-friendly availability message.
9. The `if not api_data.get("current") ...` check refuses incomplete answers. It is better to explain that data is incomplete than to crash later when a field is used.
10. It returns a smaller dictionary with only `location`, `current`, `daily`, and `timezone`. This common dictionary is called `weather_data` in the rest of the project.

### `location_label(weather_data)`

**Purpose:** create a neat label such as `Phagwara, Punjab, India`.

1. It reads the saved `location` dictionary.
2. It places the name, first administrative area (state/province), and country into a list.
3. It loops through that list, ignoring empty parts and duplicate text.
4. `", ".join(...)` joins the remaining parts with commas.

This lets the screen be specific about which API city result it used.

### `today_rain_probability(weather_data)`

**Purpose:** safely read today’s maximum forecast precipitation probability.

The daily response stores values in lists. Index `0` means the first day (today). The function first gets the list with a default empty list. It returns the first value only when the list is available; otherwise, it returns `None`. `None` means “not available,” not zero percent.

### `forecast_rows(weather_data, number_of_days=3)`

**Purpose:** make rows for Streamlit’s forecast table.

The API sends parallel lists, for example:

```text
time:        [day 1, day 2, day 3]
max temp:    [value 1, value 2, value 3]
rain chance: [value 1, value 2, value 3]
```

1. The function gets the first `number_of_days` dates.
2. It loops with `enumerate`, which gives both the position (`index`) and the date (`date_text`).
3. It formats the date using `datetime.strptime`. If formatting fails, it simply uses the original API text.
4. For each list, it verifies that the index exists before reading it. That stops an incomplete API list causing an `IndexError`.
5. It sends the WMO code to `weather_description`.
6. It creates one simple dictionary with Date, Condition, Min / Max, and Rain chance.
7. It returns a list of these row dictionaries for `st.dataframe`.

### `short_forecast_text(weather_data)`

**Purpose:** make a brief forecast sentence for the chat response.

1. It reuses `forecast_rows`, so the table and chat use the same API values.
2. If there are no rows, it returns a clear unavailable message.
3. A list comprehension changes each row into a short sentence.
4. `"; ".join(sentences)` combines the sentences.

Using a template is safer and clearer than asking a language model to invent a weather statement.

## 4. `alerts.py` — threshold comparisons

### Constants

```python
HIGH_TEMPERATURE_C = 40
LOW_TEMPERATURE_C = 5
HIGH_RAIN_PROBABILITY_PERCENT = 70
```

Keeping thresholds at the top makes the rules visible and easy to modify. In a classroom, call them **teaching thresholds**, not official warnings.

### `create_alerts(weather_data)`

**Purpose:** create alert dictionaries when a returned value crosses a threshold.

1. It starts with `alerts = []`, an empty list.
2. It reads current temperature and calls `today_rain_probability`.
3. If temperature is at least 40, it adds a heat-alert dictionary.
4. `elif` means the cold rule is checked only if the heat rule did not already match. A temperature cannot realistically be both at least 40 and at most 5.
5. It separately checks rain probability. It is not `elif` because a city can have both a temperature alert and a rain alert.
6. It returns the list. An empty list means no rule was triggered.

Each alert dictionary contains `level` and `message`. The UI uses `level` to choose a warning or information box.

## 5. `chatbot.py` — question rules and answer templates

### `CLIMATE_EXPLANATION`

This is a fixed educational paragraph. It explains that **weather** is short-term atmospheric conditions and **climate** is a long-term pattern, normally measured over 30 years or more. The text also honestly says that this app is mainly a weather app.

### `detect_intent(question)`

**Purpose:** label a question with one supported intent.

1. `.lower().strip()` turns `" What Is The Temperature? "` into lower-case, clean text. That means keyword matching does not fail just because a user used capital letters or spaces.
2. Each `if`/`elif` condition uses `any(word in text for word in [...])`. `any` returns `True` when at least one keyword from that list appears.
3. The order is important:
   - alerts and climate are checked first because their words are more specific;
   - forecast is checked before rain so `Will it rain tomorrow?` becomes a forecast question;
   - humidity, rain, temperature, and general current weather follow;
   - if no rule matches, it returns `unsupported`.
4. The function returns only a label such as `"rain"`; it does not fetch any data or write the full answer.

This separation makes it easy to test. It is also easy to explain its limitation: the word matching may not understand unusual wording or spelling mistakes.

### `_format_alerts(alerts)`

**Purpose:** turn the list returned by `create_alerts` into chat text.

1. If `alerts` is empty, return a clear “No threshold alerts” message.
2. Otherwise, read each alert’s `message` with a list comprehension and join them with spaces.

The underscore at the start is a Python convention that means this helper is intended for use inside `chatbot.py`, not as the main public function.

### `answer_question(question, weather_data, alerts)`

**Purpose:** select a response template and fill it with API data.

1. It calls `detect_intent(question)`.
2. It reads common values once: selected city label, temperature, humidity, feels-like temperature, wind, weather condition, and rain probability.
3. An `if`/`elif` chain chooses the matching answer.
4. For a forecast, it calls `short_forecast_text`, which uses the forecast API data.
5. For alerts, it passes through the list created by `create_alerts`.
6. For unsupported text, it tells the user which topics are supported and gives an example. It does not make up a response.

The output is a normal Python string. `app.py` displays it in the assistant chat bubble.

## 6. `app.py` — the Streamlit website

### `st.set_page_config(...)`

This configures the browser tab title, emoji icon, and wide page layout. It must be called before most Streamlit output commands.

### `initialise_session_state()`

**Purpose:** create remembered variables the first time the app runs.

Streamlit reruns the script after interactions. `st.session_state` is like a small dictionary that survives those reruns for the same browser session.

- `weather_data` starts as `None`; it will later hold the selected city’s API response.
- `messages` starts as an empty list; it holds chat bubbles.
- `question_history` starts as an empty list; it feeds the sidebar list.

The `if "name" not in st.session_state` checks avoid erasing information on every rerun.

### `load_weather(city_name)`

**Purpose:** run the API request after the user selects the button.

1. `st.spinner` gives the user visual feedback while the request is running.
2. It calls `get_weather_for_city` and saves the returned dictionary in session state.
3. It clears old chat messages so they do not describe a previous city.
4. It shows a success message with `location_label`.
5. `except CityNotFoundError` displays the specific city message.
6. `except WeatherServiceError` displays the network or incomplete-data message.

### `show_weather_dashboard(weather_data)`

**Purpose:** show the selected city’s live summary, alerts, and forecast.

1. It reads the current data and today’s rain probability.
2. It calls `create_alerts` once.
3. `st.columns(4)` creates four side-by-side metric cards: temperature, humidity, rain chance, and condition.
4. For each alert, it uses `st.warning` for a High alert and `st.info` for a Medium alert.
5. If there are none, it shows a success message.
6. It makes the forecast table with `forecast_rows`.
7. Finally, it returns `alerts` so the chat can answer alert questions with the same rules.

### `show_chat(weather_data, alerts)`

**Purpose:** display old messages and process one new chat question.

1. It loops through `st.session_state.messages` and displays each one with `st.chat_message`.
2. `st.chat_input` displays the text field at the bottom of the chat area.
3. When the user submits a question, it saves a user message and puts the question at position zero in `question_history`.
4. `[:8]` keeps only the latest eight questions.
5. It calls `answer_question(question, weather_data, alerts)`.
6. It saves and displays the answer as an assistant message.

### `main()`

**Purpose:** arrange the whole page in the correct order.

1. Calls `initialise_session_state` first.
2. Shows the title and the honest “not a trained generative AI” note.
3. Builds the sidebar: city input, load button, and question history.
4. Reads `weather_data` from session state.
5. If it is `None`, it tells the user to load a city first.
6. Otherwise, it calls the dashboard and chat functions.
7. It always shows the climate note and Open-Meteo attribution.

### `if __name__ == "__main__": main()`

This standard Python pattern runs `main()` when `app.py` is started directly by Streamlit. It avoids running the page automatically if another Python file imports this module later.

## 7. `tests/test_logic.py` — confidence without an internet connection

The test file uses an intentionally fake `SAMPLE_WEATHER_DATA` dictionary. That is correct for a unit test because the aim is to verify the rules, not test live weather. Important tests include:

- A question containing both `rain` and `tomorrow` gets the `forecast` intent.
- A known temperature question gets the `temperature` intent.
- An unknown question gets `unsupported`.
- 42°C plus 80% rain probability triggers heat and rain alerts.
- Safe values produce an empty alert list.
- The answer template includes the supplied temperature.
- The forecast helper makes three rows and translates a WMO code.

Run them with `python -m unittest discover -s tests -v` from the project folder.

## 8. How to explain the project honestly in a viva

Say this:

> “The project uses an API for the actual weather measurements and forecast. My own Python logic does not predict the weather. It classifies a small number of question types with keywords and uses fixed `if`/`elif` rules for responses and alerts. I chose this approach because it is transparent, beginner-friendly, and easy to test. A future version could use a trained intent classifier, but it would need labelled data and proper evaluation.”

That answer shows both technical understanding and appropriate limits.
