import requests
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/pipeline.log", encoding="utf-8"),
    ],
)

def transform_data(daily):
    df = pd.DataFrame({
        "date": daily["time"],
        "max_temperature": daily["temperature_2m_max"],
        "max_wind_speed": daily["wind_speed_10m_max"],
    })
    df["date"] = pd.to_datetime(df["date"])
    return df

def validate_data(df):
    required_columns = [
        "date",
        "max_temperature",
        "max_wind_speed"]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}")


    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        raise ValueError("Column 'date' must contain datetime values.")

    numeric_columns = ["max_temperature", "max_wind_speed"]

    for column in numeric_columns:
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(
                f"Column '{column}' must contain numeric values.")

    # Check for missing values
    missing_values = df.isnull()
    missing_rows = df[missing_values.any(axis=1)]

    if not missing_rows.empty:
        for index, row in missing_rows.iterrows():
            missing_columns = row.index[row.isnull()]

            for column in missing_columns:
                date = row["date"].strftime("%Y-%m-%d")
                raise ValueError(
                    f"Missing value detected. "
                    f"Location: Athens, "
                    f"Date: {date}, "
                    f"Column: {column}. "
                    f"Pipeline stopped."
                )

    # Check for negative wind speeds
    negative_wind = df["max_wind_speed"] < 0

    if negative_wind.any():
        row = df.loc[negative_wind].iloc[0]
        date = row["date"].strftime("%Y-%m-%d")

        raise ValueError(
            f"Invalid wind speed detected. "
            f"Location: Athens, "
            f"Date: {date}, "
            f"Value: {row['max_wind_speed']}. "
            f"Pipeline stopped."
        )


url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 37.9838,
    "longitude": 23.7275,
    "daily": "temperature_2m_max,wind_speed_10m_max",
    "timezone": "Europe/Athens",
    "forecast_days": 3,
}

try:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    logging.info("API request completed successfully.")
except requests.exceptions.RequestException as e:
    logging.error("API request failed: %s", e)
    raise SystemExit(f"Request failed: {e}")

data = response.json()
daily = data["daily"]

df = transform_data(daily)

validate_data(df)
logging.info("Data validation completed successfully.")

print(response.status_code)
print(df)
