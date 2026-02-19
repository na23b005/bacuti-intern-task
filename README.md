# Corporate Sustainability Reporting Dashboard

## Overview

The **Corporate Sustainability Reporting Dashboard** is a data analytics tool designed to track and visualize environmental, social, and governance (ESG) metrics of Indian companies listed on the NSE. 

## Features

-   **Automated Data Ingestion**: Scrapes the latest BRSR XBRL filings directly from the NSE India repository.
-   **XBRL Parsing Engine**: Extracts complex data points like Scope 1, 2, & 3 emissions, turnover, and energy consumption from raw XML/XBRL files.
-   **PostgreSQL Integration**: Robust data storage using a relational database for efficient querying.
-   **Executive Dashboard**:
    -   **Emission Intensity Leaderboard**: Ranks companies based on Carbon Intensity (tCO2e / Revenue).
    -   **Renewable Energy Tracker**: Visualizes the shift towards green energy sources.

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

The application connects to a PostgreSQL database using a connection string.

1.  Create a `.streamlit/secrets.toml` file in the project root (if running locally).
2.  Add your `DATABASE_URL`:

```toml
DATABASE_URL = "postgresql://username:password@hostname:port/database_name"
```

> **Note:** For Streamlit Cloud deployment, add this `DATABASE_URL` in the "Secrets" section of your app settings.

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
5.  (Optional) Click **"Clear Database"** to remove all stored data.

## Live Demo

Deployment Link: [ESG Data Command Center](https://corporate-sustainablity-reports-kiukawqhkxgkdg2y33spdw.streamlit.app/)



