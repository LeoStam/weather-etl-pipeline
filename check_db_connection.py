
import logging
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

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
    host="localhost",
    port=5432,
    database=os.environ["POSTGRES_DB"],
)

engine = create_engine(database_url, pool_pre_ping=True)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        logger.info("Database connection successful: %s", result.scalar())
except Exception:
    logger.exception("Database connection failed")
    raise
finally:
    engine.dispose()
