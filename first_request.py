import requests
import pandas as pd


url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 37.9838,
    "longitude": 23.7275,
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
    "timezone": "Europe/Athens",
    "forecast_days": 3,
}

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()

print(response.status_code)
data = response.json()
daily = data["daily"]


dates = daily["time"]
max_temps = daily["temperature_2m_max"]
wind_speeds = daily["wind_speed_10m_max"]




df = pd.DataFrame({
    "date": daily["time"],
    "max_temperature": daily["temperature_2m_max"],
    "max_wind_speed": daily["wind_speed_10m_max"],
})
df["date"] = pd.to_datetime(df["date"])

print(df)


def validate_data(df):
    if df.isnull().sum().any() > 0:
        return False
    if (df["max_wind_speed"] < 0).any():
        return False
    return True

is_valid = validate_data(df)

if not is_valid:
    raise ValueError("Data validation failed. Pipeline stopped.")

print("Data is valid. Continue pipeline.")