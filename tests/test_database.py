
from unittest.mock import Mock, MagicMock

import pandas as pd
import pytest

from database import load_data


def test_load_data_skips_empty_dataframe():
    engine = Mock()
    dataframe = pd.DataFrame(
        columns=["date", "max_temperature", "max_wind_speed"]
    )

    load_data(engine, dataframe)

    engine.begin.assert_not_called()


def test_load_data_propagates_database_error():
    engine = MagicMock()
    dataframe = pd.DataFrame({
        "date": pd.to_datetime(["2026-10-27"]),
        "max_temperature": [19.2],
        "max_wind_speed": [10.8],
    })

    engine.begin.return_value.__enter__.return_value.execute.side_effect = (
        RuntimeError("Simulated database failure")
    )

    with pytest.raises(RuntimeError, match="Simulated database failure"):
        load_data(engine, dataframe)


def test_load_data_executes_statement():
    engine = MagicMock()
    dataframe = pd.DataFrame({
        "date": pd.to_datetime(["2026-10-27"]),
        "max_temperature": [19.2],
        "max_wind_speed": [10.8],
    })

    load_data(engine, dataframe)

    connection = engine.begin.return_value.__enter__.return_value

    connection.execute.assert_called_once()
    engine.begin.return_value.__exit__.assert_called_once_with(
        None, None, None
    )
