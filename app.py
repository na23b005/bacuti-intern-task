import streamlit as st

from scraper import NSEScraper
from parser import parse_xbrl_file
from database import setup_database, insert_company_data, get_connection, clear_database
import queries
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
st.markdown("Scrape the latest XBRL files from NSE and analyse data.")

st.markdown("### Data Synchronization")
if st.button("Start Processing", type="primary"):
    import glob
    import shutil
    
    xml_dir = "brsr_xmls"
    if os.path.exists(xml_dir):
        shutil.rmtree(xml_dir)
    os.makedirs(xml_dir, exist_ok=True)
    
    scraper = NSEScraper()
    status_container = st.status("Starting Sync Process...", expanded=True)
    
    try:
        setup_database() # Ensure DB exists before clearing
        
        # Clear Database First
        status_container.write("Clearing database...")
        clear_database()

        # 1. Initialize & Fetch List
        status_container.write("Initializing connection to NSE...")
        scraper.initialize()
        
        status_container.write("Fetching company list...")
        companies = scraper.get_company_list()
        
        if not companies:
            raise Exception("Failed to fetch company list from NSE.")
            
        total_companies = len(companies)
        status_container.write(f"Found {total_companies} companies. Starting pipeline...")
        
        progress_bar = st.progress(0)
        success_count = 0
        
        for i, comp in enumerate(companies):
            symbol = comp.get('symbol', 'Unknown')
            xbrl_url = comp.get('xbrlFile')
            
            # Update status
            status_container.update(label=f"Processing {i+1}/{total_companies}: {symbol}")
            
            # A. Download
            filepath = scraper.download_xbrl(symbol, xbrl_url)
            
            if filepath and os.path.exists(filepath):
                # B. Process
                try:
                    parsed_data = parse_xbrl_file(filepath, symbol)
                    insert_company_data(parsed_data)
                    success_count += 1
                except Exception as e:
                    st.warning(f"Error parsing/inserting {symbol}: {e}")
                finally:
                    # C. Cleanup File
                    if os.path.exists(filepath):
                        os.remove(filepath)
            
            progress_bar.progress((i + 1) / total_companies)
            
        status_container.update(label="Sync Complete!", state="complete", expanded=False)
        st.success(f"Sync finished. Successfully processed {success_count} companies.")
        
        # Cleanup directory if empty
        if not os.listdir(xml_dir):
            os.rmdir(xml_dir)
            
        time.sleep(1)
        st.rerun()

    except Exception as e:
        status_container.update(label="Sync Failed!", state="error")
        st.error(f"Critical Error during Sync: {e}")
        
        # Cleanup on Failure
        st.warning("Performing cleanup due to failure...")
        if os.path.exists(xml_dir):
            shutil.rmtree(xml_dir)
        clear_database()
        st.error("Cleanup complete: Database cleared and local files removed.")



# --- Section 2: KPI Overview ---
kpi_count, kpi_avg_ren = queries.get_kpi_metrics()
kpi1, kpi3 = st.columns(2)

with kpi1:
    st.metric("Companies Analyzed", value=kpi_count)
with kpi3:
    st.metric("Source", value=f"NSE India")

st.markdown("---")

# --- Section 3: Detailed Analysis Tables ---
tab1, tab2 = st.tabs(["Emission Intensity", "Renewable Energy Usage"])

with tab1:
    st.subheader("Lowest Scope 1 & 2 Emissions Intensity")
    st.caption("Metric = (Total Scope 1 + Total Scope 2) / Turnover")
    
    df_a = queries.get_emission_intensity()
    
    if not df_a.empty:
        st.dataframe(
            df_a,
            use_container_width=True,
            hide_index=True,
            column_config={
                "symbol": st.column_config.TextColumn("Symbol", width="small"),
                "company_name": st.column_config.TextColumn("Company", width="medium"),
                "scope1": st.column_config.NumberColumn("Scope 1 (KtCO2e)", format="%.2f"),
                "scope2": st.column_config.NumberColumn("Scope 2 (KtCO2e)", format="%.2f"),
                "total_emissions": st.column_config.NumberColumn("Total Emissions (KtCO2e)", format="%.2f"),
                "turnover": st.column_config.NumberColumn("Turnover (Cr INR)", format="%.2f"), 
                "intensity": st.column_config.NumberColumn(
                    "Intensity (KtCO2e / Cr INR)", 
                    help="Calculated as (Scope 1 + Scope 2) / Turnover * 10,000,000 (KtCO2e per Crore INR)",
                    format="%.2f"
                ),
            }
        )
    else:
        st.info("No data available. Run the ingestion process above.")

with tab2:
    st.subheader("Renewable Energy Adoption Leaders")
    st.caption("Metric = (Total Electricity from Renewable Sources / Total Electricity Consumption)")
    
    df_b = queries.get_renewable_leaders()
    
    if not df_b.empty:
        st.dataframe(
            df_b,
            use_container_width=True,
            hide_index=True,
            column_config={
                "symbol": st.column_config.TextColumn("Symbol", width="small"),
                "company_name": st.column_config.TextColumn("Company", width="medium"),
                "renewable_electricity": st.column_config.NumberColumn("Renewable (Gigajoule)", format="%.2f"),
                "non_renewable_electricity": st.column_config.NumberColumn("Non-Renewable (Gigajoule)", format="%.2f"),
                "total_electricity": st.column_config.NumberColumn("Total Electricity (GJ)", format="%.2f"),
                "renewable_percentage": st.column_config.NumberColumn(
                    "Renewable Share", 
                    help="Calculated as (Renewable / Total Electricity Consumption) * 100",
                    format="%.2f %%" 
                ),
            }
        )
    else:
        st.info("No data available. Run the ingestion process above.")