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
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
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
    conn.close()

def insert_company_data(data):
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO companies VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT(symbol) DO UPDATE SET
                    company_name=EXCLUDED.company_name,
                    scope1_emissions=EXCLUDED.scope1_emissions,
                    scope2_emissions=EXCLUDED.scope2_emissions,
                    scope3_emissions=EXCLUDED.scope3_emissions,
                    turnover=EXCLUDED.turnover,
                    total_electricity=EXCLUDED.total_electricity,
                    renewable_electricity=EXCLUDED.renewable_electricity,
                    non_renewable_electricity=EXCLUDED.non_renewable_electricity
            """, (
                data['symbol'],
                data['NameOfTheCompany'],
                data['TotalScope1Emissions'],
                data['TotalScope2Emissions'],
                data['TotalScope3Emissions'],
                data['Turnover'],
                data['TotalElectricityConsumption'],
                data['TotalElectricityConsumptionFromRenewableSources'],
                data['TotalElectricityConsumptionFromNonRenewableSources']
            ))
    conn.close()

def clear_database():
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE companies")
    conn.close()
