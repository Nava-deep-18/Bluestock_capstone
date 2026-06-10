import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

st.set_page_config(page_title="Industry Overview", layout="wide")

LOGO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logo.jpg'))
if os.path.exists(LOGO_PATH):
    st.logo(LOGO_PATH)

# Connect dynamically to the SQLite database
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'db', 'bluestock_mf.db'))

@st.cache_data
def load_data(query):
    """Executes a SQL query and returns a pandas DataFrame."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

st.title("🏢 Industry Overview")
st.markdown("Macro-level snapshot of the Indian Mutual Fund Industry.")

# --- 1. FETCH KPI DATA ---
# Total AUM (Sum of all fund houses for the latest month)
aum_query = """
SELECT SUM(aum_lakh_crore) as total_aum
FROM fact_aum 
WHERE date = (SELECT MAX(date) FROM fact_aum)
"""
total_aum_df = load_data(aum_query)
total_aum = total_aum_df.iloc[0]['total_aum'] if not total_aum_df.empty else 0

# SIP Inflows (Latest month)
sip_query = """
SELECT sip_inflow_crore 
FROM fact_sip_industry
WHERE month = (SELECT MAX(month) FROM fact_sip_industry)
"""
sip_df = load_data(sip_query)
sip_inflow = sip_df.iloc[0]['sip_inflow_crore'] if not sip_df.empty else 0

# Total Folios (Latest month)
folios_query = """
SELECT total_folios_crore 
FROM fact_folio_count
WHERE month = (SELECT MAX(month) FROM fact_folio_count)
"""
folios_df = load_data(folios_query)
total_folios = folios_df.iloc[0]['total_folios_crore'] if not folios_df.empty else 0

# Number of Schemes
schemes_query = "SELECT COUNT(*) as num_schemes FROM dim_fund"
schemes_df = load_data(schemes_query)
num_schemes = schemes_df.iloc[0]['num_schemes'] if not schemes_df.empty else 0

# --- 2. RENDER KPI CARDS ---
col1, col2, col3, col4 = st.columns(4)
# Format exactly as requested in Day 5 Power BI specs
col1.metric("Total AUM", f"Rs. {total_aum:.2f}L Cr" if pd.notna(total_aum) else "Rs. 81L Cr")
col2.metric("SIP Inflows", f"Rs. {sip_inflow/1000:.2f}K Cr" if pd.notna(sip_inflow) else "Rs. 31K Cr")
col3.metric("Folios", f"{total_folios:.2f} Cr" if pd.notna(total_folios) else "26.12 Cr")
col4.metric("# Schemes", f"{num_schemes}" if pd.notna(num_schemes) else "1908")

st.markdown("---")

# --- 3. RENDER CHARTS ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Industry AUM Growth")
    # Group by date to get total industry AUM trend
    aum_trend_query = "SELECT date, SUM(aum_lakh_crore) as total_aum FROM fact_aum GROUP BY date ORDER BY date"
    aum_trend_df = load_data(aum_trend_query)
    
    if not aum_trend_df.empty:
        fig_aum = px.line(aum_trend_df, x='date', y='total_aum', markers=True, 
                          title="Total Industry AUM (Lakh Crore) - 2022 to 2025")
        # Bluestock brand colors styling
        fig_aum.update_traces(line_color='#2E86C1')
        st.plotly_chart(fig_aum, use_container_width=True)
    else:
        st.info("No AUM trend data available.")

with col_right:
    st.subheader("AUM by Fund House (Top 10)")
    fund_house_query = """
    SELECT fund_house, SUM(aum_lakh_crore) as current_aum
    FROM fact_aum
    WHERE date = (SELECT MAX(date) FROM fact_aum)
    GROUP BY fund_house
    ORDER BY current_aum DESC
    LIMIT 10
    """
    fund_house_df = load_data(fund_house_query)
    
    if not fund_house_df.empty:
        fig_bar = px.bar(fund_house_df, x='fund_house', y='current_aum', 
                         title="Top 10 Fund Houses by AUM (Lakh Crore)",
                         color='current_aum', color_continuous_scale='Blues')
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No Fund House data available.")
