import requests
from datetime import date, timedelta
from models.schema import WeatherSummary

def summarize_weather(lat: float, lon: float, location_name: str) -> WeatherSummary:
    """Call Open-Meteo and return a helpful natural summary for tomorrow."""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
    )
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    # Grab first day in response
    tmax = float(data["daily"]["temperature_2m_max"][0])
    tmin = float(data["daily"]["temperature_2m_min"][0])
    advice = "Layer up." if tmin < 8 else "Light jacket should be fine."
    summary = f"Tomorrow in {location_name}: high {tmax:.1f}°C, low {tmin:.1f}°C."
    return WeatherSummary(
        location=location_name,
        date=tomorrow,
        summary=summary,
        high_c=tmax,
        low_c=tmin,
        advice=advice
    )

