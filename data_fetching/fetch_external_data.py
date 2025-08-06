# ================================
# fetch_external_data.py
# ================================
import requests
import datetime

# ---- Weather API ----
OPENWEATHER_API_KEY = "196363664c9d4e7c506063ab62d33f21"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/forecast"

# ---- Festival API ----
CALENDARIFIC_API_KEY = "NcUaO9vlpxzP0rwsS2Pr94oRxusirYOx"
CALENDARIFIC_URL = "https://calendarific.com/api/v2/holidays"


def get_weather(city, date):
    """
    Fetch weather forecast for a city on a given date.
    Returns one of: Clear, Rain, Fog, Storm.
    Fallback -> 'Clear' if API fails.
    """
    try:
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        response = requests.get(OPENWEATHER_URL, params=params, timeout=5)
        data = response.json()
        forecast_list = data.get("list", [])

        target_date = date if isinstance(date, datetime.date) else datetime.datetime.strptime(date, "%Y-%m-%d").date()

        for item in forecast_list:
            forecast_date = datetime.datetime.fromtimestamp(item["dt"]).date()
            if forecast_date == target_date:
                weather_condition = item["weather"][0]["main"].lower()
                if "rain" in weather_condition:
                    return "Rain"
                elif "fog" in weather_condition or "mist" in weather_condition or "haze" in weather_condition:
                    return "Fog"
                elif "storm" in weather_condition or "thunder" in weather_condition:
                    return "Storm"
                else:
                    return "Clear"
        return "Clear"
    except Exception as e:
        print(f"Weather API error: {e}")
        return "Clear"


def get_festival_impact(date):
    """
    Fetch if date is holiday/festival using Calendarific.
    Returns FestivalDay, FestivalEve, or None.
    Fallback -> 'None' if API fails.
    """
    try:
        params = {
            "api_key": CALENDARIFIC_API_KEY,
            "country": "IN",
            "year": date.year,
            "month": date.month,
            "day": date.day
        }
        response = requests.get(CALENDARIFIC_URL, params=params, timeout=5)
        data = response.json()
        holidays = data.get("response", {}).get("holidays", [])
        if holidays:
            return "FestivalDay"
        return "None"
    except Exception as e:
        print(f"Festival API error: {e}")
        return "None"
