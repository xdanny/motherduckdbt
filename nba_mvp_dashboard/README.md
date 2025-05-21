# NBA MVP Dashboard

## Overview

This project fetches NBA player statistics for the 2023 season from [Basketball-Reference.com](https://www.basketball-reference.com/), processes and transforms this data using dbt (Data Build Tool) with a DuckDB backend, and then presents the insights via an interactive Streamlit dashboard. The primary goal is to identify and display potential NBA MVP candidates based on their regular season performance statistics.

## Technologies Used

*   **Python 3.x**
*   **pandas:** For data manipulation and analysis.
*   **requests:** For fetching HTML content from the web.
*   **Beautiful Soup (bs4):** For parsing HTML and extracting data.
*   **dbt-core & dbt-duckdb:** For data transformation and modeling.
*   **DuckDB:** As the analytical data warehouse.
*   **Streamlit:** For creating and serving the interactive web dashboard.
*   **lxml:** As an HTML parser for pandas `read_html`.

## Project Structure

The project is organized as follows:

```
nba_mvp_dashboard/
├── data/                     # Stores raw CSV data and the DuckDB database file.
│   ├── nba_2023_per_game_stats.csv
│   └── nba_analytics.duckdb
├── dbt_project/
│   └── nba_dbt_project/      # Contains the dbt project.
│       ├── models/           # dbt models (staging, intermediate, marts).
│       │   ├── staging/
│       │   ├── intermediate/
│       │   └── marts/
│       ├── profiles.yml      # dbt profile configuration (uses DuckDB).
│       └── dbt_project.yml   # dbt project configuration.
├── scripts/                  # Python scripts for tasks like data fetching.
│   └── fetch_data.py
├── streamlit_app/            # Contains the Streamlit application.
│   └── app.py
└── README.md                 # This file.
```

*   `data/`: Holds the raw data fetched from the web (e.g., `nba_2023_per_game_stats.csv`) and the DuckDB database file (`nba_analytics.duckdb`) created by dbt.
*   `dbt_project/nba_dbt_project/`: The core dbt project.
    *   `models/`: Contains SQL definitions for dbt models, organized into:
        *   `staging/`: Models for cleaning and basic transformation of raw source data.
        *   `intermediate/`: Models for more complex transformations or aggregations.
        *   `marts/`: Data marts for specific analytical purposes (e.g., MVP candidates).
*   `scripts/`: Contains standalone Python scripts. `fetch_data.py` is used to scrape data from Basketball-Reference.com.
*   `streamlit_app/`: Contains the Python script (`app.py`) for the Streamlit web dashboard.

## Setup Instructions

### Prerequisites

*   Python 3.7 or higher.
*   pip (Python package installer).

### Installation

1.  **Clone the repository** (or ensure you have the project files if you are already in the environment):
    *(If you're running this in a provided environment, the files are likely already present.)*
    ```bash
    # git clone <repository_url>
    # cd nba_mvp_dashboard
    ```

2.  **Navigate to the project root directory:**
    If you've just cloned, you should already be there. The root directory is `nba_mvp_dashboard/`.

3.  **Install Python dependencies:**
    It's recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
    Then, install the required packages:
    ```bash
    pip install pandas requests beautifulsoup4 dbt-core dbt-duckdb streamlit lxml
    ```

## Running the Project

Follow these steps in order to fetch data, transform it, and view the dashboard.

### Step 1: Fetch Data

This step uses the `fetch_data.py` script to scrape player per-game statistics for the 2023 NBA season from [Basketball-Reference.com](https://www.basketball-reference.com/).

1.  Ensure you are in the project root directory (`nba_mvp_dashboard/`).
2.  Run the script:
    ```bash
    python scripts/fetch_data.py
    ```
3.  This will create (or overwrite) the `nba_mvp_dashboard/data/nba_2023_per_game_stats.csv` file.

### Step 2: Run dbt Models

This step processes the raw CSV data, transforms it using dbt, and loads it into the DuckDB data warehouse (`nba_mvp_dashboard/data/nba_analytics.duckdb`).

1.  Navigate to the dbt project directory:
    ```bash
    cd dbt_project/nba_dbt_project/
    ```
2.  Run the dbt models:
    ```bash
    dbt run --profiles-dir .
    ```
    The `--profiles-dir .` flag tells dbt to look for `profiles.yml` in the current directory. This command will build all models (staging, intermediate, and marts).

3.  (Optional but recommended) Generate dbt documentation:
    ```bash
    dbt docs generate --profiles-dir .
    ```
    You can then view the documentation by running `dbt docs serve --profiles-dir .` and opening the provided URL in your browser.

4.  Navigate back to the project root directory:
    ```bash
    cd ../..
    ```

### Step 3: Launch Streamlit Dashboard

This step starts the Streamlit web application to view the MVP candidates and their statistics.

1.  Ensure you are in the project root directory (`nba_mvp_dashboard/`).
2.  Run the Streamlit application:
    ```bash
    streamlit run streamlit_app/app.py
    ```
3.  Streamlit will typically open the dashboard automatically in your default web browser. If not, it will display a local URL (e.g., `http://localhost:8501`) that you can navigate to.

## dbt Project Details

The dbt project (`dbt_project/nba_dbt_project/`) is configured to use DuckDB. The database file is stored at `data/nba_analytics.duckdb`.

Key dbt models include:
*   **`models/sources.yml`**: Defines the raw CSV data (`player_per_game_stats`) as a source for dbt.
*   **`models/staging/stg_player_per_game_stats.sql`**: Cleans the raw data, casts data types, renames columns, and filters out invalid rows (e.g., header rows from the scrape).
*   **`models/intermediate/int_player_stats_summary.sql`**: Selects key columns from the staging model, providing a summarized view of player statistics.
*   **`models/marts/mvp_candidates.sql`**: Filters players from `int_player_stats_summary` based on MVP-relevant criteria (e.g., minimum games played, minimum points per game) and orders them.

## Future Enhancements

*   **User-selectable seasons:** Allow users to choose different NBA seasons for analysis.
*   **Advanced MVP criteria:** Implement more sophisticated filtering or scoring logic for MVP candidacy.
*   **More visualizations:** Add charts for player comparison, trend analysis, or team performance context.
*   **Player profile pages:** Clicking on a player could lead to a more detailed statistics page.
*   **Enhanced data fetching:** Add error resilience, logging, and potentially support for other data sources.
*   **Comprehensive dbt tests:** Add more specific data quality tests to the dbt models.

---
This README provides a guide to understanding, setting up, and running the NBA MVP Dashboard project.
