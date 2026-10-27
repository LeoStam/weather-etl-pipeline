# Weather ETL Pipeline

A beginner-friendly Data Engineering portfolio project that extracts weather forecast data from the Open-Meteo API, transforms and validates it with Python and Pandas, and loads it into PostgreSQL.

The project demonstrates practical ETL development, relational database operations, data validation, idempotent loading, error handling, logging, automated testing, and reproducible local setup.

## Project Overview

The pipeline follows four main steps:

1. **Extract:** Retrieve daily weather forecast data from the Open-Meteo REST API.
2. **Transform:** Convert the API response into a structured Pandas DataFrame.
3. **Validate:** Check the required columns, data types, missing values, and wind-speed values.
4. **Load:** Store the validated records in PostgreSQL using SQLAlchemy.

The pipeline retrieves a three-day weather forecast for Athens, Greece. Forecast values may change between executions.

## Data Source

The project uses the [Open-Meteo Forecast API](https://open-meteo.com/en/docs), which provides weather forecast data without requiring an API key for eligible non-commercial use.

Current request configuration:

| Parameter | Value |
|---|---|
| Latitude | `37.9838` |
| Longitude | `23.7275` |
| Time zone | `Europe/Athens` |
| Forecast period | 3 days |

Daily variables retrieved from the API:

| API variable | Description |
|---|---|
| `temperature_2m_max` | Maximum daily temperature |
| `wind_speed_10m_max` | Maximum daily wind speed |

The pipeline transforms these values into the following DataFrame columns:

| Column | Description |
|---|---|
| `date` | Forecast date, represented as a Pandas datetime before loading |
| `max_temperature` | Maximum daily temperature |
| `max_wind_speed` | Maximum daily wind speed |

## Technology Stack

- **Python 3** — pipeline implementation
- **Requests** — HTTP communication with the API
- **Pandas** — data transformation and validation
- **PostgreSQL** — relational database
- **SQLAlchemy** — database connectivity, schema definition, and data loading
- **Psycopg 3** — PostgreSQL driver
- **Docker Compose** — local PostgreSQL environment
- **python-dotenv** — loading local environment variables
- **Python logging** — execution monitoring and error reporting
- **Pytest** — automated tests
- **Git and GitHub** — version control and portfolio development

## Project Structure

```text
weather-etl-pipeline/
├── .gitignore
├── .env.example
├── compose.yaml
├── requirements.txt
├── README.md
├── first_request.py
├── database.py
├── setup_database.py
├── check_db_connection.py
└── tests/
    ├── test_api.py
    ├── test_database.py
    ├── test_transform.py
    └── test_validation.py
```

Local files such as `.env`, `.venv/`, Python cache files, pytest cache files, and execution logs are excluded from version control.

## Prerequisites

Before running the project, make sure you have:

- Python 3 installed
- Git installed
- Docker Desktop with Docker Compose available
- Internet access to reach the Open-Meteo API

The instructions below use Windows PowerShell.

## Installation and Setup

### 1. Clone the repository

Replace the placeholder with the URL of your GitHub repository.

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd weather-etl-pipeline
```

If you are already working in the local repository, skip this step.

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

Check the installed packages for dependency conflicts:

```powershell
python -m pip check
```

### 4. Configure environment variables

Create a local `.env` file from the example template:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and configure the PostgreSQL database credentials:

```dotenv
POSTGRES_DB=weather_db
POSTGRES_USER=weather_user
POSTGRES_PASSWORD=replace_with_a_local_password
```

These are example values, not credentials to reuse in a shared or production environment. Choose your own local password.

The application and Docker Compose configuration require all three environment variables. The database connection code checks that they are present before creating the SQLAlchemy engine.

**Security note:** The `.env` file contains local configuration and must not be committed to Git. The `.gitignore` file excludes it. The `.env.example` file contains placeholder values and can be committed safely.

### 5. Prepare the logging directory

The pipeline writes execution logs to `logs/pipeline.log`. Create the directory if it does not already exist:

```powershell
New-Item -ItemType Directory -Force logs
```

### 6. Start PostgreSQL

From the project root, start the database container:

```powershell
docker compose up -d
```

Check the service status:

```powershell
docker compose ps
```

View PostgreSQL logs if necessary:

```powershell
docker compose logs db
```

The Compose configuration uses the `postgres:17` image, publishes PostgreSQL on `127.0.0.1:5432`, stores database files in a named volume, and defines a health check.

The database port is bound to the local IPv4 loopback interface. The Python application connects to PostgreSQL through `127.0.0.1`.

## Running the Pipeline

Make sure Docker Compose is running and the `.env` file is configured.

Execute:

```powershell
python first_request.py
```

The pipeline performs the following operations:

1. Sends a GET request to the Open-Meteo API with a 10-second timeout.
2. Checks the HTTP response using `raise_for_status()`.
3. Parses the JSON response.
4. Transforms the daily forecast into a Pandas DataFrame.
5. Validates the required columns, data types, missing values, and wind speeds.
6. Creates the `weather_forecast` table if it does not exist.
7. Loads the validated records into PostgreSQL.
8. Logs execution results and prints the HTTP status and DataFrame.

A successful run should report that the API request and data validation completed successfully, the database table is ready, and the pipeline finished.

The returned forecast values may differ between runs.

## Data Validation

The `validate_data()` function checks that:

- All required columns are present.
- The `date` column has a datetime data type.
- Temperature and wind-speed columns have numeric data types.
- Required values are not missing.
- Maximum wind speed is not negative.

A validation failure raises a `ValueError` and stops the normal pipeline flow before the database load.

## Database Schema

The `database.py` module defines the `weather_forecast` table using SQLAlchemy Core.

| Column | SQLAlchemy type | Constraint |
|---|---|---|
| `date` | `Date` | Primary key |
| `max_temperature` | `Float` | `NOT NULL` |
| `max_wind_speed` | `Float` | `NOT NULL` |

The `date` column is the primary key because the pipeline stores one daily forecast record per date.

The `create_table(engine)` function uses `metadata.create_all()` to create the table if it does not exist. It does not automatically migrate the schema of an existing table.

## Database Loading and Duplicate Prevention

The `load_data(engine, dataframe)` function:

1. Skips the database write when the DataFrame is empty.
2. Copies the DataFrame and converts the date values to Python date objects.
3. Converts the rows into records.
4. Uses PostgreSQL `INSERT ... ON CONFLICT DO UPDATE` through SQLAlchemy's PostgreSQL dialect.
5. Executes the write inside an `engine.begin()` transaction.

The primary key enforces uniqueness by date. If a date already exists, the upsert updates its `max_temperature` and `max_wind_speed` values instead of inserting a duplicate row.

The transaction commits when the operation completes successfully and rolls back if an exception occurs within the transaction context.

The SQLAlchemy engine is disposed of after the database load attempt.

This makes repeated executions idempotent for the dates being loaded. Dates that are no longer returned by the API are not automatically deleted; older records remain in the table unless explicitly removed.

## Verify the Stored Data

### View the saved forecast records

The following examples use the database and username configured in the setup instructions:

```powershell
docker compose exec db psql -U weather_user -d weather_db -c "SELECT date, max_temperature, max_wind_speed FROM weather_forecast ORDER BY date;"
```

### Check the number of records per date

```powershell
docker compose exec db psql -U weather_user -d weather_db -c "SELECT date, COUNT(*) FROM weather_forecast GROUP BY date ORDER BY date;"
```

Each stored date should have a count of `1`.

### Check for duplicate dates

```powershell
docker compose exec db psql -U weather_user -d weather_db -c "SELECT date, COUNT(*) FROM weather_forecast GROUP BY date HAVING COUNT(*) > 1;"
```

The query should return no rows.

### Verify idempotency manually

1. Start PostgreSQL.
2. Run `python first_request.py`.
3. Run `python first_request.py` again.
4. Query the database and verify that there is only one record per date.

This check was performed during development. Two consecutive successful pipeline executions produced three records in PostgreSQL, one per forecast date, and the duplicate-date query returned no rows.

### Reset the local database when needed

To stop and remove the Compose containers and delete the named database volume:

```powershell
docker compose down -v
```

Start PostgreSQL again:

```powershell
docker compose up -d
```

**Warning:** `docker compose down -v` permanently deletes the persisted database data for this Compose project. Use it only when you intentionally want a clean database.

To stop the database without deleting its persisted data, use:

```powershell
docker compose down
```

## Logging and Error Handling

Python's logging module writes messages to the terminal and `logs/pipeline.log`.

The pipeline logs:

- Successful API requests
- API request failures
- Successful data validation
- Database table readiness
- Database load execution
- Pipeline completion

The API request uses a timeout and `raise_for_status()` to detect request failures. Request exceptions are logged and stop normal execution.

Database operations use a transaction. Database exceptions stop normal execution, and the SQLAlchemy engine is disposed of after the load attempt.

Execution logs are excluded from version control.

## Automated Testing

The project uses Pytest to test the transformation, validation, API failure handling, and database-loading behavior.

Run the full test suite from the project root:

```powershell
python -m pytest -v
```

The automated tests cover:

| Test module | Coverage |
|---|---|
| `tests/test_transform.py` | Expected output columns, values, and date data type |
| `tests/test_validation.py` | Valid data, missing columns, non-numeric temperature values, missing values, and negative wind speeds |
| `tests/test_api.py` | API connection failure stops pipeline execution |
| `tests/test_database.py` | Empty DataFrame handling and propagation of database errors |

The database tests use mocks for the relevant loading scenarios, so these tests do not require a running PostgreSQL database.

The current test suite contains **10 passing tests**.

The project also underwent a manual end-to-end verification using a fresh PostgreSQL volume. The pipeline was executed twice successfully, the records were queried directly from PostgreSQL, and no duplicate dates were found.

## Additional Database Utilities

Two utility scripts are included:

- `setup_database.py` — database setup utility.
- `check_db_connection.py` — utility for checking database connectivity.

These scripts support local database setup and troubleshooting.

## Current Project Status

### Completed

- Open-Meteo API integration
- HTTP timeout and status checking
- API request error handling and logging
- Data transformation with Pandas
- Data validation for required columns, data types, missing values, and negative wind speeds
- PostgreSQL setup using Docker Compose
- SQLAlchemy database connection using environment variables
- `weather_forecast` table definition and creation
- Transactional database loading
- Duplicate prevention with a primary key and PostgreSQL upsert
- Safe pipeline imports using a `main()` entry point
- Automated Pytest coverage for the main transformation, validation, API failure, and database-loading scenarios
- Manual end-to-end verification and repeated-execution checks
- Environment-variable template and Git ignore configuration

### Remaining work

- Final repository review and Git commit
- GitHub Actions workflow for automated testing
- Documented automated or scheduled execution strategy
- Final portfolio review

GitHub Actions cannot directly connect to a PostgreSQL database running only on a personal computer. Automated tests should therefore run independently of the local database, while any future workflow requiring PostgreSQL must provision an accessible database as part of its execution environment.

Scheduled execution should be implemented only with a practical, documented approach that does not assume a personal computer or its local database is always available.

## Learning Goals

This project is designed to demonstrate an understandable end-to-end Data Engineering workflow and to support discussion of the following topics in a technical interview:

- How data moves through an ETL pipeline
- How API responses are transformed and validated
- How Python connects to PostgreSQL
- How transactions and database constraints protect data integrity
- How upserts prevent unintended duplicate records
- How logging and error handling support troubleshooting
- How automated tests validate pipeline behavior
- How environment variables and Git protect local configuration
- How to separate local development infrastructure from automated CI execution

## License and API Usage

This project uses the Open-Meteo Forecast API. Review the [Open-Meteo documentation](https://open-meteo.com/en/docs) and its applicable terms for details about data usage and attribution.
