# Weather ETL Pipeline

A beginner-friendly data engineering project that extracts weather forecast data from the Open-Meteo API, transforms it with Python and Pandas, validates data quality, and records execution events using Python logging.

The pipeline is being developed incrementally, with the goal of loading processed data into PostgreSQL and supporting automated testing and execution.

## Project Overview

This project demonstrates the core stages of an ETL (Extract, Transform, Load) pipeline:

1. **Extract:** Retrieve weather forecast data from a public REST API.
2. **Transform:** Convert the API response into a structured Pandas DataFrame.
3. **Validate:** Check the schema, data types, missing values, and wind speed values.
4. **Load:** Planned for a future stage using PostgreSQL.

The project is designed to demonstrate practical data engineering skills through a small, understandable implementation.

## Data Source

The pipeline uses the [Open-Meteo Forecast API](https://api.open-meteo.com/v1/forecast).

The API provides weather forecast data without requiring an API key for eligible non-commercial use.

The current request retrieves a three-day daily forecast for Athens, Greece.

| Parameter | Value |
|---|---|
| Latitude | `37.9838` |
| Longitude | `23.7275` |
| Time zone | `Europe/Athens` |
| Forecast period | 3 days |

The requested daily weather variables are:

- `temperature_2m_max` — maximum daily temperature
- `wind_speed_10m_max` — maximum daily wind speed

Forecast dates and values may change between executions.

## Current Technology Stack

- **Python 3** — pipeline implementation
- **Requests** — HTTP communication with the API
- **Pandas** — data transformation and validation
- **Python logging** — execution messages and error reporting
- **Git** — version control
- **GitHub** — intended portfolio repository

A Python virtual environment (`.venv`) is used to isolate project dependencies.

PostgreSQL, SQLAlchemy, Docker Compose, Pytest, and GitHub Actions are planned for later stages.

## Project Structure

```text
weather-etl-pipeline/
├── .gitignore
├── README.md
├── first_request.py
├── logs/
│   └── pipeline.log
└── .venv/
```

The `.venv/` directory contains the local Python environment and should not be committed to Git.

The `logs/` directory stores the local execution log. It is excluded from version control through `.gitignore`.

## Current Implementation

### 1. API Extraction

The pipeline sends an HTTP GET request to the Open-Meteo API using the Requests library.

The request includes a 10-second timeout and uses `response.raise_for_status()` to detect unsuccessful HTTP status codes.

API request failures are logged, and the script exits with an error message.

### 2. Data Transformation

The API's daily forecast response is transformed into a Pandas DataFrame containing:

| Column | Description |
|---|---|
| `date` | Forecast date, converted to a datetime value |
| `max_temperature` | Maximum daily temperature |
| `max_wind_speed` | Maximum daily wind speed |

The transformation logic is implemented in `transform_data()`.

### 3. Data Validation

The `validate_data()` function currently checks that:

- All required columns exist.
- The `date` column contains datetime values.
- Temperature and wind speed columns contain numeric values.
- No required data values are missing.
- Maximum wind speed is not negative.

If validation fails, the function raises a `ValueError`, stopping normal execution.

### 4. Logging and Error Handling

Python's logging module records messages to both the terminal and `logs/pipeline.log`.

The current implementation logs:

- Successful API requests.
- API request failures.
- Successful data validation.

HTTP request exceptions are handled and logged before the script exits.

## Requirements

- Python 3
- Internet access to reach the Open-Meteo API
- Git (optional, for version control)

## Setup and Usage

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd weather-etl-pipeline
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with the actual repository URL. If you are working from an existing local repository, skip this step.

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install the required packages

```powershell
python -m pip install requests pandas
```

### 4. Run the pipeline

From the project root, execute:

```powershell
python first_request.py
```

A successful execution should log the API request and validation results and print the HTTP status code and the resulting DataFrame.

The forecast values depend on the API response at the time of execution.

## Current Project Status

### Completed

- Initial Open-Meteo API integration
- HTTP request timeout and status checking
- API request error handling and logging
- JSON response parsing
- DataFrame creation and date conversion
- Separate transformation and validation functions
- Required-column and data-type checks
- Missing-value validation
- Negative wind speed validation
- Logging to the terminal and a local log file
- Git repository initialization

### Planned

- Refactor the code into separate extraction, transformation, and loading modules
- Add automated tests using Pytest
- Configure PostgreSQL and Docker Compose
- Connect to PostgreSQL using SQLAlchemy
- Implement transactional database loading
- Prevent duplicate records across repeated executions
- Improve documentation and setup instructions as the pipeline grows
- Configure automated testing and a practical scheduled execution approach

## Learning Objectives

This project is intended to build practical experience with:

- REST API integration
- Data transformation and quality validation
- Python error handling and logging
- Relational database loading
- Idempotent ETL design
- Automated testing
- Version control and reproducible project setup

The implementation prioritizes correctness, readability, and a clear understanding of each pipeline stage over unnecessary complexity.
