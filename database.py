
import logging
import os

from dotenv import load_dotenv
from sqlalchemy import (
    URL,
    Column,
    Date,
    Float,
    MetaData,
    Table,
    create_engine,
)
from sqlalchemy.dialects.postgresql import insert

logger = logging.getLogger(__name__)

load_dotenv()

metadata = MetaData()

weather_forecast = Table(
    "weather_forecast",
    metadata,
    Column("date", Date, primary_key=True),
    Column("max_temperature", Float, nullable=False),
    Column("max_wind_speed", Float, nullable=False),
)


def get_engine():
    required_variables = [
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]

    missing_variables = [
        name for name in required_variables if not os.getenv(name)
    ]

    if missing_variables:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing_variables)}"
        )

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host="127.0.0.1",
        port=5432,
        database=os.environ["POSTGRES_DB"],
    )

    return create_engine(database_url, pool_pre_ping=True)


def create_table(engine):
    metadata.create_all(engine, tables=[weather_forecast])
    logger.info("Table weather_forecast is ready.")


def load_data(engine, dataframe):
    if dataframe.empty:
        logger.info("No weather data to load.")
        return

    records = dataframe.copy()
    records["date"] = records["date"].dt.date
    records = records.to_dict(orient="records")

    statement = insert(weather_forecast).values(records)

    statement = statement.on_conflict_do_update(
        index_elements=["date"],
        set_={
            "max_temperature": statement.excluded.max_temperature,
            "max_wind_speed": statement.excluded.max_wind_speed,
        },
    )

    with engine.begin() as connection:
        result = connection.execute(statement)

    logger.info("Weather data loaded successfully. Rows affected: %s", result.rowcount)
