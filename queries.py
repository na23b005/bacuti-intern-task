from database import get_connection
from tabulate import tabulate
import pandas as pd

def run_queries():
    conn = get_connection()
    cur = conn.cursor()

    print("\nTop 10 Lowest Emissions Intensity")
    cur.execute("""
        SELECT company_name,
               ROUND(((scope1_emissions + scope2_emissions) / NULLIF(turnover,0)) * 10000000, 4)
        FROM companies
        WHERE turnover > 0
        ORDER BY 2 ASC LIMIT 10
    """)
    print(tabulate(cur.fetchall(), headers=["Company","Intensity"]))

    print("\nTop Renewable Leaders")
    cur.execute("""
        SELECT company_name,
               ROUND((renewable_electricity / NULLIF(total_electricity,0)) * 100, 2)
        FROM companies
        WHERE total_electricity > 0
        ORDER BY 2 DESC LIMIT 10
    """)
    print(tabulate(cur.fetchall(), headers=["Company","% Renewable"]))

    conn.close()

def get_dataframe(query):
    conn = get_connection()
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        conn.close()

def get_kpi_metrics():
    conn = get_connection()
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            count = pd.read_sql_query("SELECT COUNT(*) as c FROM companies", conn).iloc[0]['c']
            avg_ren = pd.read_sql_query("SELECT AVG(renewable_electricity / NULLIF(total_electricity,0)) as a FROM companies", conn).iloc[0]['a']
        return count, (avg_ren * 100) if avg_ren else 0
    except:
        return 0, 0
    finally:
        conn.close()

def get_emission_intensity():
    # Intensity in KtCO2e / Cr INR
    # Scope 1, 2, Total in KtCO2e (Database stores in Kt)
    # Turnover in Cr INR (divide by 1e7)
    # Intensity = (Total) / (Turnover / 1e7) = (Total / Turnover) * 10,000,000

    query = '''
        SELECT symbol,
               company_name,
               scope1_emissions as scope1,
               scope2_emissions as scope2,
               (scope1_emissions + scope2_emissions) as total_emissions,
               turnover / 10000000.0 as turnover,
               ((scope1_emissions + scope2_emissions) / NULLIF(turnover,0)) * 10000000 as intensity
        FROM companies
        WHERE turnover > 0
        ORDER BY intensity ASC, symbol ASC
        LIMIT 10
    '''
    return get_dataframe(query)

def get_renewable_leaders():
    query = '''
        SELECT symbol,
            company_name,
            renewable_electricity,
            non_renewable_electricity,
            total_electricity,
            (renewable_electricity / NULLIF(total_electricity,0)) * 100 as renewable_percentage
        FROM companies
        WHERE total_electricity > 0
        ORDER BY renewable_percentage DESC, symbol ASC
        LIMIT 10
    '''
    return get_dataframe(query)
