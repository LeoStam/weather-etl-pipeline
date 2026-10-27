
import pandas as pd

from first_request import transform_data


def test_transform_data_returns_expected_columns_and_values():
    # Arrange: δημιουργούμε ενδεικτικά δεδομένα API
    daily = {
        "time": ["2026-10-27", "2026-10-28"],
        "temperature_2m_max": [19.2, 15.0],
        "wind_speed_10m_max": [10.8, 16.5],
    }

    # Act: εκτελούμε τη συνάρτηση που θέλουμε να ελέγξουμε
    df = transform_data(daily)

    # Assert: ελέγχουμε αν το αποτέλεσμα είναι σωστό
    assert df.columns.tolist() == [
        "date",
        "max_temperature",
        "max_wind_speed",
    ]

    assert df["max_temperature"].tolist() == [19.2, 15.0]
    assert df["max_wind_speed"].tolist() == [10.8, 16.5]

    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert len(df) == 2
