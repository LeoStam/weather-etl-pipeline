
import pandas as pd
import pytest

from first_request import validate_data


def create_valid_dataframe():
    return pd.DataFrame({
        "date": pd.to_datetime(["2026-10-27", "2026-10-28"]),
        "max_temperature": [19.2, 15.0],
        "max_wind_speed": [10.8, 16.5],
    })


def test_validate_data_accepts_valid_dataframe():
    df = create_valid_dataframe()

    result = validate_data(df)

    assert result is None


def test_validate_data_rejects_missing_column():
    df = create_valid_dataframe()
    df = df.drop(columns=["max_temperature"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_data(df)


def test_validate_data_rejects_non_numeric_temperature():
    df = create_valid_dataframe()
    df["max_temperature"] = ["warm", 15.0]

    with pytest.raises(ValueError, match="must contain numeric values"):
        validate_data(df)


def test_validate_data_rejects_missing_values():
    df = create_valid_dataframe()
    df.loc[0, "max_temperature"] = float("nan")

    with pytest.raises(ValueError, match="Missing value detected"):
        validate_data(df)


def test_validate_data_rejects_negative_wind_speed():
    df = create_valid_dataframe()
    df.loc[0, "max_wind_speed"] = -5.0

    with pytest.raises(ValueError, match="Invalid wind speed detected"):
        validate_data(df)
