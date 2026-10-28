# Weather ETL Pipeline

An end-to-end Data Engineering portfolio project that extracts daily weather forecasts from the Open-Meteo REST API, transforms and validates the data with Python and Pandas, and loads it into PostgreSQL.

The project demonstrates practical ETL development, relational database operations, data validation, idempotent loading, error handling, logging, automated testing, Docker-based local development, and continuous integration with GitHub Actions.

## Project Overview

The pipeline follows these steps:

1. **Extract** daily weather forecast data from the Open-Meteo REST API.
2. **Transform** the API response into a structured Pandas DataFrame.
3. **Validate** the required columns, data types, missing values, and wind-speed values.
4. **Load** validated records into PostgreSQL using SQLAlchemy.
5. **Log** execution progress and errors.

The current configuration retrieves a three-day forecast for Athens, Greece. Forecast values can change between executions.

## Data Source

This project uses the [Open-Meteo Forecast API](https://open-meteo.com/en/docs). The API does not require an API key for eligible use. Review Open-Meteo's current terms and attribution requirements before using or redistributing the data.

### Request Configuration

| Parameter | Value |
|---|---|
| Latitude | `37.9838` |
| Longitude | `23.7275` |
| Time zone | `Europe/Athens` |
| Forecast period | 3 days |

### Daily Variables

| API Variable | Description | DataFrame / Database Field |
|---|---|---|
| `temperature_2m_max` | Maximum daily temperature | `max_temperature` |
| `wind_speed_10m_max` | Maximum daily wind speed | `max_wind_speed` |
| API daily date | Forecast date | `date` |

The pipeline stores one row per forecast date. When a date is returned again, its stored forecast values are updated instead of creating a second row. This design keeps the latest forecast for each date; it does not preserve a history of forecast revisions.

## Technology Stack

- **Python 3** — pipeline implementation
- **Requests** — HTTP requests to the API
- **Pandas** — data transformation and validation
- **PostgreSQL** — relational data storage
- **SQLAlchemy** — database connectivity, table definition, and loading
- **Psycopg 3** — PostgreSQL driver
- **Docker Compose** — local PostgreSQL environment
- **python-dotenv** — environment-variable configuration
- **Python logging** — execution monitoring and error reporting
- **Pytest** — automated testing
- **Git and GitHub** — version control and portfolio
- **GitHub Actions** — automated test execution on pushes and pull requests

## Project Structure

```text
weather-etl-pipeline/
├── .github/
│   └── workflows/
│       └── tests.yml
├── tests/
│   ├── test_api.py
│   ├── test_database.py
│   ├── test_transform.py
│   └── test_validation.py
├── .env.example
├── .gitignore
├── compose.yaml
├── requirements.txt
├── README.md
├── first_request.py
├── database.py
├── setup_database.py
└── check_db_connection.py
```

Local-only files such as `.env`, `.venv/`, Python cache files, pytest cache files, and execution logs are excluded from version control.

## Prerequisites

Before running the project, install:

- Python 3
- Git
- Docker Desktop with Docker Compose
- Internet access to reach the Open-Meteo API

The commands below use Windows PowerShell.

## Installation and Setup

### 1. Clone the Repository

```powershell
git clone https://github.com/LeoStam/weather-etl-pipeline.git
cd weather-etl-pipeline
```

If you already have a local clone, open PowerShell in the project directory and skip this step.

### 2. Create and Activate a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation because of its execution policy, you can run the virtual environment's Python directly:

```powershell
.\.venv\Scripts\python.exe --version
```

This avoids changing the system-wide execution policy.

### 3. Install Dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

### 4. Configure Environment Variables

Create a local `.env` file from the example template:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and configure the database credentials. For example:

```dotenv
POSTGRES_DB=weather_db
POSTGRES_USER=weather_user
POSTGRES_PASSWORD=choose_a_local_password
```

These are example values. Choose your own local password.

Both Docker Compose and the Python database configuration use these variables. The application checks that the required variables are present before creating the SQLAlchemy engine.

**Security:** Never commit `.env` or real credentials. The repository's `.gitignore` excludes `.env`, while `.env.example` is intended to contain placeholders only.

### 5. Start PostgreSQL

From the project root, run:

```powershell
docker compose up -d
```

Check the service status:

```powershell
docker compose ps
```

Check whether PostgreSQL is accepting connections:

```powershell
docker compose exec db pg_isready
```

View the database container logs if necessary:

```powershell
docker compose logs db
```

The Compose configuration uses the `postgres:17` image, publishes the database on `127.0.0.1:5432`, stores database files in a named Docker volume, and defines a health check. The Python application connects to PostgreSQL through `127.0.0.1`.

The pipeline creates the `logs/` directory automatically when it starts, so no manual logging-directory setup is required.

## Running the Pipeline

With Docker Compose running and `.env` configured, execute:

```powershell
python first_request.py
```

The pipeline:

1. Sends a GET request to Open-Meteo with a 10-second timeout.
2. Checks the HTTP response using `raise_for_status()`.
3. Parses the JSON response.
4. Transforms the daily forecast into a Pandas DataFrame.
5. Validates the data.
6. Creates the `weather_forecast` table if it does not already exist.
7. Loads the records into PostgreSQL.
8. Logs execution details and reports the response status and resulting data.

A successful run should report that the API request and validation succeeded, the database table is ready, and the pipeline completed. Forecast values may differ between runs.

## Data Transformation and Validation

The transformation step maps the API's daily fields to a DataFrame with these columns:

- `date`
- `max_temperature`
- `max_wind_speed`

The `validate_data()` function checks that:

- All required columns are present.
- The `date` column uses a datetime data type.
- Temperature and wind-speed fields have numeric data types.
- Required values are not missing.
- Maximum wind speed is not negative.

A validation failure raises a `ValueError` and prevents the normal pipeline flow from reaching the database load.

## Database Schema

The `database.py` module defines the `weather_forecast` table using SQLAlchemy Core.

| Column | Type | Constraint |
|---|---|---|
| `date` | `Date` | Primary key |
| `max_temperature` | `Float` | `NOT NULL` |
| `max_wind_speed` | `Float` | `NOT NULL` |

The `date` column is the primary key because the pipeline stores one current forecast record per date. The `create_table(engine)` function uses SQLAlchemy metadata to create the table if it does not exist; it is not a schema-migration tool.

## Database Loading and Duplicate Prevention

The `load_data(engine, dataframe)` function:

1. Skips the database write when the DataFrame is empty.
2. Copies the DataFrame and converts dates to Python `date` objects.
3. Converts the rows into records.
4. Uses PostgreSQL `INSERT ... ON CONFLICT DO UPDATE`.
5. Executes the write inside an `engine.begin()` transaction.

The primary key enforces uniqueness by date. If the same date is loaded again, the upsert updates its temperature and wind-speed values rather than inserting a duplicate row.

The transaction commits if the operation succeeds and rolls back if an exception occurs inside the transaction context. Database errors are allowed to propagate so the pipeline can report a failed execution. The SQLAlchemy engine is disposed of after the load attempt.

This makes repeated executions idempotent with respect to duplicate dates. Dates that are no longer returned by the API are not automatically deleted, so older dates can remain in the table.

## Verify the Stored Data

The following commands use the example database and username from the setup section. If you chose different values, update the commands accordingly.

### View the Forecast Records

```powershell
docker compose exec db psql -U weather_user -d weather_db -c "SELECT date, max_temperature, max_wind_speed FROM weather_forecast ORDER BY date;"
```

### Count Records per Date

```powershell
docker compose exec db psql -U weather_user -d weather_db -c "SELECT date, COUNT(*) FROM weather_forecast GROUP BY date ORDER BY date;"
```

Each stored date should have a count of `1`.

### Check for Duplicate Dates

```powershell
docker compose exec db psql -U weather_user -d weather_db -c "SELECT date, COUNT(*) FROM weather_forecast GROUP BY date HAVING COUNT(*) > 1;"
```

The query should return no rows.

### Manually Verify Repeated Execution

1. Start PostgreSQL.
2. Run `python first_request.py`.
3. Run `python first_request.py` a second time.
4. Query the database and check that there is only one row per date.

During development, two consecutive successful executions produced three rows in PostgreSQL, one per forecast date, and the duplicate-date query returned no rows.

### Reset the Local Database

To stop the Compose containers and delete the named database volume:

```powershell
docker compose down -v
```

Start PostgreSQL again:

```powershell
docker compose up -d
```

**Warning:** `docker compose down -v` deletes the persisted database data for this Compose project. Use it only when you intentionally want to reset the database.

To stop the database without deleting its persisted data, use:

```powershell
docker compose down
```

## Logging and Error Handling

The Python `logging` module writes messages to the terminal and to `logs/pipeline.log`.

The pipeline logs key events, including:

- Successful API requests
- API request failures
- Successful data validation
- Database table readiness
- Database loading
- Pipeline completion

The API request has a timeout and checks HTTP status codes. Request exceptions are logged and stop normal execution. Database operations run inside a transaction; database exceptions stop normal execution, and the SQLAlchemy engine is disposed of after the load attempt.

The `logs/` directory and its contents are excluded from version control.

## Automated Tests

Run the full test suite from the project root:

```powershell
python -m pytest -v
```

The tests cover the following areas:

| Test Module | Coverage |
|---|---|
| `tests/test_transform.py` | Output columns, transformed values, and date data type |
| `tests/test_validation.py` | Valid data, missing columns, non-numeric temperature values, missing values, and negative wind speeds |
| `tests/test_api.py` | API connection failure stops pipeline execution |
| `tests/test_database.py` | Empty DataFrame handling, database error propagation, and loading behavior |

Database-loading tests use mocks for the tested scenarios, so the test suite does not require a running PostgreSQL database.

The current test suite has **10 passing tests** in the local development environment.

The project has also undergone a manual end-to-end check against PostgreSQL: the pipeline ran successfully twice, the stored records were queried, and no duplicate dates were found.

## Continuous Integration with GitHub Actions

The workflow in `.github/workflows/tests.yml` runs the automated tests on pushes and pull requests.

The CI job installs the Python dependencies and runs:

```bash
python -m pytest -v
```

The tests are designed to run without a PostgreSQL server, so GitHub Actions does not need to connect to a database running on a personal computer.

**CI scope:** This workflow verifies the automated test suite. It does not run the complete ETL pipeline against a live PostgreSQL database.

## Database Utility Scripts

Two utility scripts are included:

- `setup_database.py` — database setup utility.
- `check_db_connection.py` — checks database connectivity.

They are available for local setup and troubleshooting.

## Current Project Status

The core ETL pipeline has been implemented and tested.

Completed functionality includes:

- Open-Meteo API extraction
- HTTP timeout and status checking
- API request error handling and logging
- Pandas transformation and data validation
- PostgreSQL environment using Docker Compose
- SQLAlchemy connection configured through environment variables
- `weather_forecast` table definition and creation
- Transactional database loading
- Duplicate prevention using a primary key and PostgreSQL upsert
- Main-entry-point structure for safe imports
- Automated tests for transformation, validation, API failure, and database-loading behavior
- Manual end-to-end verification and repeated-run checks
- `.env.example` and `.gitignore` configuration
- GitHub repository and GitHub Actions test workflow

**Scheduling:** Automated scheduled execution is not included in the current implementation. The pipeline can be run manually with `python first_request.py` when PostgreSQL is available.

## Learning Goals

This project is designed to support practical discussion of these Data Engineering topics in a technical interview:

- How data moves through an ETL pipeline
- How API responses are transformed and validated
- How Python connects to PostgreSQL
- How database constraints and transactions protect data integrity
- How upserts prevent unintended duplicate records
- How logging and error handling support troubleshooting
- How automated tests validate pipeline behavior
- How environment variables and Git help protect local configuration
- How local development infrastructure differs from a CI environment

## API Usage and License

This project uses the [Open-Meteo Forecast API](https://open-meteo.com/en/docs). Review the current [Open-Meteo terms](https://open-meteo.com/en/terms) and applicable attribution requirements before redistributing or using the data beyond personal development.

This repository does not currently declare a separate software license.
