import psycopg2
import os
import streamlit as st

def get_connection():

    # Priority 1 — Streamlit secrets
    if "DATABASE_URL" in st.secrets:
        return psycopg2.connect(st.secrets["DATABASE_URL"])

    # Priority 2 — env variable (local dev)
    if os.getenv("DATABASE_URL"):
        return psycopg2.connect(os.getenv("DATABASE_URL"))

    raise Exception("Database connection not configured")

# Default fallback params (kept for backward compatibility if needed)
DB_PARAMS = {
    "dbname": "bacuti",
    "user": "postgres",
    "password": "asd", 
    "host": "localhost",
    "port": "5432"
}

def setup_database():
    """
    Creates the schema.
    Discussion Q8 Improvement: We are using NUMERIC instead of REAL. 
    NUMERIC is exact and prevents the floating-point rounding errors 
    that can occur with SQLite's REAL data type.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_emissions (
            symbol VARCHAR(100) PRIMARY KEY,
            company_name TEXT,
            website TEXT,
            scope1_emissions NUMERIC,
            scope2_emissions NUMERIC,
            scope3_emissions NUMERIC,
            turnover NUMERIC,
            total_electricity NUMERIC,
            renewable_electricity NUMERIC,
            non_renewable_electricity NUMERIC
        )
    ''')
    conn.commit()
    
    # Migration for existing table
    try:
        cursor.execute('ALTER TABLE company_emissions ADD COLUMN IF NOT EXISTS non_renewable_electricity NUMERIC')
        conn.commit()
    except Exception:
        conn.rollback()

    cursor.close()
    conn.close()

def insert_company_data(data):
    """Inserts or updates company data in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Error Handling Example (Discussion Q6): Postgres uses ON CONFLICT DO UPDATE 
    # to handle upserts. If we run the script twice, it updates rather than crashing.
    insert_query = '''
        INSERT INTO company_emissions (
            symbol, company_name, website, scope1_emissions, scope2_emissions, 
            scope3_emissions, turnover, total_electricity, renewable_electricity,
            non_renewable_electricity
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (symbol) DO UPDATE SET
            company_name = EXCLUDED.company_name,
            website = EXCLUDED.website,
            scope1_emissions = EXCLUDED.scope1_emissions,
            scope2_emissions = EXCLUDED.scope2_emissions,
            scope3_emissions = EXCLUDED.scope3_emissions,
            turnover = EXCLUDED.turnover,
            total_electricity = EXCLUDED.total_electricity,
            renewable_electricity = EXCLUDED.renewable_electricity,
            non_renewable_electricity = EXCLUDED.non_renewable_electricity;
    '''
    
    # Notice we are passing floats/strings mapped from the dictionary
    cursor.execute(insert_query, (
        data.get('symbol'), data.get('NameOfTheCompany'), data.get('WebsiteOfCompany'),
        data.get('TotalScope1Emissions'), data.get('TotalScope2Emissions'), 
        data.get('TotalScope3Emissions'), data.get('Turnover'),
        data.get('TotalElectricityConsumption'), data.get('TotalElectricityConsumptionFromRenewableSources'),
        data.get('TotalElectricityConsumptionFromNonRenewableSources')
    ))
    
    conn.commit()
    cursor.close()
    conn.close()

def clear_database():
    """Truncates the company_emissions table."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("TRUNCATE TABLE company_emissions")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()