import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(page_title="SIP & Market Trends", layout="wide")

LOGO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logo.jpg'))
if os.path.exists(LOGO_PATH):
    st.logo(LOGO_PATH)

# Connect dynamically to the SQLite database
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'db', 'bluestock_mf.db'))

@st.cache_data
def load_data(query):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

st.title("📈 SIP & Market Trends")
st.markdown("Analyze industry-wide SIP inflows, category performance, and market benchmarks.")

# --- 1. FETCH DATA ---
sip_query = "SELECT * FROM fact_sip_industry"
sip_df = load_data(sip_query)

cat_inflows_query = "SELECT * FROM fact_category_inflows"
cat_df = load_data(cat_inflows_query)

bench_query = "SELECT * FROM fact_benchmark WHERE index_name = 'NIFTY50'"
bench_df = load_data(bench_query)

if sip_df.empty or cat_df.empty or bench_df.empty:
    st.error("Missing necessary data in the database.")
    st.stop()

# --- 2. KPI ---
st.markdown("### Industry KPIs")

# Convert strings to floats
try:
    sip_df['yoy_growth_pct'] = sip_df['yoy_growth_pct'].astype(float)
    sip_df['active_sip_accounts_crore'] = sip_df['active_sip_accounts_crore'].astype(float)
    sip_df['sip_inflow_crore'] = sip_df['sip_inflow_crore'].astype(float)
except:
    pass

latest_sip = sip_df.sort_values('month').iloc[-1]
yoy_growth = latest_sip.get('yoy_growth_pct', 0.0)
total_accounts = latest_sip.get('active_sip_accounts_crore', 0.0)
latest_inflow = latest_sip.get('sip_inflow_crore', 0.0)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total SIP Accounts (Crore)", f"{total_accounts:.2f}", f"{yoy_growth:.2f}% YoY Growth")
with col2:
    st.metric("Latest Monthly SIP Inflow (Crore)", f"₹{latest_inflow:,.0f}")

st.markdown("---")

# --- 3. CHARTS ---
row1_col1, row1_col2 = st.columns(2)

# Chart 1: Dual-axis SIP Inflow (bar) + Nifty 50 (line)
with row1_col1:
    st.subheader("SIP Inflow vs Nifty 50 Growth")
    # Clean dates and ensure numeric types
    sip_df['date'] = pd.to_datetime(sip_df['month'], format='mixed', errors='coerce')
    bench_df['date'] = pd.to_datetime(bench_df['date'], format='mixed', errors='coerce')
    bench_df['close_value'] = pd.to_numeric(bench_df['close_value'], errors='coerce')
    
    # Aggregate benchmark to monthly (only aggregating close_value to avoid TypeError on strings)
    bench_monthly = bench_df.set_index('date').resample('ME')['close_value'].mean().reset_index()
    bench_monthly['month_str'] = bench_monthly['date'].dt.strftime('%Y-%m')
    sip_df['month_str'] = sip_df['date'].dt.strftime('%Y-%m')
    
    # Merge them
    merged_df = pd.merge(sip_df, bench_monthly, on='month_str', how='inner').sort_values('date_x')
    
    fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_dual.add_trace(
        go.Bar(x=merged_df['date_x'], y=merged_df['sip_inflow_crore'], name="SIP Inflow (Cr)", marker_color="#3498DB"),
        secondary_y=False,
    )
    
    fig_dual.add_trace(
        go.Scatter(x=merged_df['date_x'], y=merged_df['close_value'], name="NIFTY 50", line=dict(color="#E74C3C", width=3)),
        secondary_y=True,
    )
    fig_dual.update_layout(hovermode="x unified")
    st.plotly_chart(fig_dual, use_container_width=True)

# Chart 2: Heat map Category inflows by month
with row1_col2:
    st.subheader("Category Net Inflows Heatmap")
    cat_df['date'] = pd.to_datetime(cat_df['month'], format='mixed', errors='coerce')
    # Sort dates to ensure chronological order in the heatmap
    cat_df = cat_df.sort_values('date')
    cat_df['month_name'] = cat_df['date'].dt.strftime('%Y-%m')
    cat_df['net_inflow_crore'] = cat_df['net_inflow_crore'].astype(float)
    
    # Pivot table for heatmap
    pivot_cat = cat_df.pivot_table(index='category', columns='month_name', values='net_inflow_crore', aggfunc='sum').fillna(0)
    
    fig_heat = px.imshow(
        pivot_cat,
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# Chart 3: Top 5 categories by net inflow FY25
st.subheader("Top 5 Categories by Net Inflow (FY25)")
# Filter for FY25 (assuming dates >= 2024-04-01 and <= 2025-03-31)
fy25_df = cat_df[(cat_df['date'] >= '2024-04-01') & (cat_df['date'] <= '2025-03-31')]

if not fy25_df.empty:
    top_5 = fy25_df.groupby('category')['net_inflow_crore'].sum().reset_index().sort_values('net_inflow_crore', ascending=False).head(5)
    fig_top5 = px.bar(
        top_5,
        x='category',
        y='net_inflow_crore',
        color='net_inflow_crore',
        color_continuous_scale="Viridis",
        labels={'net_inflow_crore': 'Net Inflow (Crore)', 'category': 'Mutual Fund Category'}
    )
    st.plotly_chart(fig_top5, use_container_width=True)
else:
    st.info("No data available for FY25.")
