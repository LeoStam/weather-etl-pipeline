
import logging
from time import perf_counter

from sqlalchemy import text

from database import create_table, get_engine

logging.basicConfig(level=logging.INFO)

start = perf_counter()
engine = get_engine()
print(f"Engine creation: {perf_counter() - start:.2f} seconds")

try:
    start = perf_counter()

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(f"SELECT 1 result: {result.scalar()}")

    print(f"Database connection and query: {perf_counter() - start:.2f} seconds")

    start = perf_counter()
    create_table(engine)
    print(f"Table setup: {perf_counter() - start:.2f} seconds")

finally:
    engine.dispose()
