# Corporate Sustainability Reporting (BRSR) Dashboard

## Overview

The **Corporate Sustainability Reporting (BRSR) Dashboard** is a data analytics tool designed to track and visualize environmental, social, and governance (ESG) metrics of Indian companies listed on the NSE. 

It automates the extraction of **Business Responsibility and Sustainability Reports (BRSR)** via XBRL files, parses key emission and energy data, and presents actionable insights through an interactive Streamlit dashboard.

## Features

-   **Automated Data Ingestion**: Scrapes the latest BRSR XBRL filings directly from the NSE India repository.
-   **XBRL Parsing Engine**: Extracts complex data points like Scope 1, 2, & 3 emissions, turnover, and energy consumption from raw XML/XBRL files.
-   **PostgreSQL Integration**: Robust data storage using a relational database for efficient querying.
-   **Executive Dashboard**:
    -   **KPI Monitor**: Tracks total companies analyzed and average renewable energy adoption.
    -   **Emission Intensity Leaderboard**: Ranks companies based on Carbon Intensity (tCO2e / Revenue).
    -   **Renewable Energy Tracker**: Visualizes the shift towards green energy sources.
-   **Cloud Ready**: Configured for easy deployment on Streamlit Community Cloud.

## Tech Stack

-   **Frontend**: [Streamlit](https://streamlit.io/)
-   **Backend Logic**: Python
-   **Database**: PostgreSQL
-   **Data Processing**: Pandas, BeautifulSoup4, LXML
-   **Data Source**: National Stock Exchange (NSE) of India

## Setup & Installation

### Prerequisites

-   Python 3.8+
-   PostgreSQL installed and running locally (or a cloud instance).

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Set Up Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database

1.  Open **pgAdmin** or `psql` and create a new database named `bacuti`.
2.  Update the credentials in `database.py` if running locally:

```python
DB_PARAMS = {
    "dbname": "bacuti",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}
```

## Running the Application

To start the dashboard:

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

## Data Synchronization

1.  Open the dashboard.
2.  Navigate to the **Data Synchronization & Ingestion** section.
3.  Click **"Load Companies Data"**.
4.  The system will download, parse, and store the latest reports automatically.



