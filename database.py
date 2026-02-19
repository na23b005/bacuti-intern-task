import psycopg2
import os
import streamlit as st

def get_connection():

    if "DATABASE_URL" in st.secrets:
        return psycopg2.connect(st.secrets["DATABASE_URL"])

    if os.getenv("DATABASE_URL"):
        return psycopg2.connect(os.getenv("DATABASE_URL"))

    raise Exception("Database connection not configured")


def setup_database():
    """Create table if not exists."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                # Check for table schema: if 'symbol' is missing, it's the old schema -> Drop it.
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='companies' AND column_name='symbol'
                """)
                # If symbol is NOT found, we must drop the table to recreate it with symbol
                if not cursor.fetchone():
                    cursor.execute("DROP TABLE IF EXISTS companies")
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS companies (
                        symbol TEXT PRIMARY KEY,
                        company_name TEXT,
                        scope1_emissions NUMERIC,
                        scope2_emissions NUMERIC,
                        scope3_emissions NUMERIC,
                        turnover NUMERIC,
                        total_electricity NUMERIC,
                        renewable_electricity NUMERIC,
                        non_renewable_electricity NUMERIC
                    )
                """)
    finally:
        conn.close()

def insert_company_data(data):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO companies (
                        symbol, company_name, scope1_emissions, scope2_emissions,
                        scope3_emissions, turnover, total_electricity,
                        renewable_electricity, non_renewable_electricity
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol) DO UPDATE SET
                        company_name = EXCLUDED.company_name,
                        scope1_emissions = EXCLUDED.scope1_emissions,
                        scope2_emissions = EXCLUDED.scope2_emissions,
                        scope3_emissions = EXCLUDED.scope3_emissions,
                        turnover = EXCLUDED.turnover,
                        total_electricity = EXCLUDED.total_electricity,
                        renewable_electricity = EXCLUDED.renewable_electricity,
                        non_renewable_electricity = EXCLUDED.non_renewable_electricity;
                """, (
                    data.get('symbol'),
                    data.get('NameOfTheCompany'),
                    data.get('TotalScope1Emissions'),
                    data.get('TotalScope2Emissions'),
                    data.get('TotalScope3Emissions'),
                    data.get('Turnover'),
                    data.get('TotalElectricityConsumption'),
                    data.get('TotalElectricityConsumptionFromRenewableSources'),
                    data.get('TotalElectricityConsumptionFromNonRenewableSources')
                ))
    finally:
        conn.close()

def clear_database():
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE companies")
    finally:
        conn.close()
