import streamlit as st
import pandas as pd
from scraper import NSEScraper
from parser import parse_xbrl_file
from database import setup_database, insert_company_data, get_connection, clear_database
import os
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="ESG Data Command Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Professional Styling ---
st.markdown("""
    <style>
        .block-container {padding-top: 2rem;}
        div[data-testid="stMetricValue"] {font-size: 24px;}
        .stDataFrame {border: 1px solid #f0f2f6; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def get_data(query):
    """Fetch data from DB with error handling."""
    conn = get_connection()
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        conn.close()

def get_kpis():
    """Fetch high-level stats for the top banner."""
    conn = get_connection()
    try:
        count = pd.read_sql_query("SELECT COUNT(*) as c FROM company_emissions", conn).iloc[0]['c']
        avg_ren = pd.read_sql_query("SELECT AVG(renewable_electricity / NULLIF(total_electricity,0)) as a FROM company_emissions", conn).iloc[0]['a']
        return count, (avg_ren * 100) if avg_ren else 0
    except:
        return 0, 0
    finally:
        conn.close()

# --- Sidebar ---
with st.sidebar:
    st.header("System Status")
    
    # DB Check
    try:
        conn = get_connection()
        conn.close()
        st.success("🟢 Database Connected")
    except:
        st.error("🔴 Database Disconnected")
        st.caption("Check PostgreSQL service on localhost:5432")

# --- Main Content ---
st.title("Corporate Sustainability Reporting")
st.markdown("### Executive Dashboard")

# --- Section 1: Data Synchronization (Collapsible) ---
st.subheader("Data Synchronization & Ingestion")
st.markdown("Use this module to scrape the latest XBRL files from NSE and analyse data.")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Load Companies Data", type="primary"):
        scraper = NSEScraper()
        
        # Initialize status with a generic title
        with st.status("Initializing Ingestion Pipeline...", expanded=True) as status:
            setup_database()
            scraper.initialize()
            
            companies = scraper.get_company_list()
            
            if not companies:
                status.update(label="Failed to fetch company list", state="error")
                st.error("Could not retrieve ticker data from NSE.")
            else:
                total = len(companies)
                processed_count = 0
                progress_bar = st.progress(0)
                
                for i, comp in enumerate(companies):
                    symbol = comp.get('symbol', 'Unknown')
                    xbrl_url = comp.get('xbrlFile')
                    
                    # UPDATE STATUS LABEL DIRECTLY: Prevents the scrolling wall of text
                    status.update(label=f"Processing {i+1}/{total}: {symbol}...")
                    
                    filepath = scraper.download_xbrl(symbol, xbrl_url)
                    
                    if filepath:
                        try:
                            parsed_data = parse_xbrl_file(filepath, symbol)
                            insert_company_data(parsed_data)
                            processed_count += 1
                        except Exception as e:
                            st.warning(f"Parse error for {symbol}: {e}")
                        finally:
                            if os.path.exists(filepath):
                                os.remove(filepath)
                    
                    progress_bar.progress((i + 1) / total)
                
                status.update(label="Ingestion Complete", state="complete", expanded=False)
                st.success(f"Pipeline finished. Successfully processed {processed_count} reports.")
                time.sleep(1)
                st.rerun()

with col2:
    if st.button("Clear Database", type="secondary"):
        try:
            clear_database()
            st.success("Database has been cleared successfully.")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing database: {e}")

# --- Section 2: KPI Overview ---
kpi_count, kpi_avg_ren = get_kpis()
kpi1, kpi3 = st.columns(2)

with kpi1:
    st.metric("Companies Analyzed", value=kpi_count)
with kpi3:
    st.metric("Data Source", value="NSE India")

st.markdown("---")

# --- Section 3: Detailed Analysis Tables ---
tab1, tab2 = st.tabs(["Emission Intensity", "Renewable Energy Usage"])

with tab1:
    st.subheader("Lowest Scope 1 & 2 Emissions Intensity")
    st.caption("Metric = (Total Scope 1 + Total Scope 2) / Turnover")
    
    # Exact Formula implementation: (Scope1 + Scope2) / Turnover
    query_a = '''
        SELECT company_name, 
               scope1_emissions,
               scope2_emissions,
               (scope1_emissions + scope2_emissions) as total_emissions,
               turnover / 10000000.0 as turnover,
               ((scope1_emissions + scope2_emissions) / turnover) * 10000000 AS intensity 
        FROM company_emissions 
        WHERE turnover > 0 AND (scope1_emissions + scope2_emissions) > 0
        ORDER BY intensity ASC 
        LIMIT 20
    '''
    
    df_a = get_data(query_a)
    
    if not df_a.empty:
        st.dataframe(
            df_a,
            use_container_width=True,
            hide_index=True,
            column_config={
                "company_name": st.column_config.TextColumn("Company", width="medium"),
                "scope1_emissions": st.column_config.NumberColumn("Scope 1 (tCO2e)", format="%.2f"),
                "scope2_emissions": st.column_config.NumberColumn("Scope 2 (tCO2e)", format="%.2f"),
                "total_emissions": st.column_config.NumberColumn("Total Emissions (tCO2e)", format="%.2f"),
                "turnover": st.column_config.NumberColumn("Turnover (Cr INR)", format="₹ %.2f"), 
                "intensity": st.column_config.NumberColumn(
                    "Intensity (tCO2e / Cr INR)", 
                    help="Calculated as (Scope 1 + Scope 2) / Turnover * 10^7 (Per Crore INR)",
                    format="%.4f"
                ),
            }
        )
    else:
        st.info("No data available. Run the ingestion process above.")

with tab2:
    st.subheader("Renewable Energy Adoption Leaders")
    st.caption("Metric = (Total Electricity from Renewable Sources / Total Electricity Consumption)")
    
    # Exact Formula implementation returning a clean percentage
    query_b = '''
        SELECT company_name, 
               renewable_electricity,
               non_renewable_electricity,
               total_electricity,
               (renewable_electricity / total_electricity) * 100 AS renewable_percentage 
        FROM company_emissions 
        WHERE total_electricity > 0 
        ORDER BY renewable_percentage DESC 
        LIMIT 20
    '''
    
    df_b = get_data(query_b)
    
    if not df_b.empty:
        st.dataframe(
            df_b,
            use_container_width=True,
            hide_index=True,
            column_config={
                "company_name": st.column_config.TextColumn("Company", width="medium"),
                "renewable_electricity": st.column_config.NumberColumn("Renewable (Gigajoule)", format="%.2f"),
                "non_renewable_electricity": st.column_config.NumberColumn("Non-Renewable (Gigajoule)", format="%.2f"),
                "total_electricity": st.column_config.NumberColumn("Total Energy (Gigajoule)", format="%.2f"),
                "renewable_percentage": st.column_config.NumberColumn(
                    "Renewable Share", 
                    help="Calculated as (Renewable / Total Electricity Consumption) * 100",
                    format="%.2f %%" 
                ),
            }
        )
    else:
        st.info("No data available. Run the ingestion process above.")