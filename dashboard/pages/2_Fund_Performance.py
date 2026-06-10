import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(page_title="Fund Performance", layout="wide")

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

st.title("📈 Fund Performance")
st.markdown("Detailed risk-return analysis and benchmark comparisons.")

# --- 1. FETCH DATA FOR SLICERS ---
perf_query = "SELECT * FROM fact_performance"
perf_df = load_data(perf_query)

if perf_df.empty:
    st.error("No performance data found in the database.")
    st.stop()

# --- 2. TOP SLICERS (FILTERS) ---
st.markdown("### Filter Options")
col1, col2, col3 = st.columns(3)

# Fund House Filter
all_houses = perf_df['fund_house'].dropna().unique().tolist()
with col1:
    selected_houses = st.multiselect("Fund House", options=all_houses, default=all_houses)

# Category Filter
all_categories = perf_df['category'].dropna().unique().tolist()
with col2:
    selected_categories = st.multiselect("Category", options=all_categories, default=all_categories)

# Plan Filter
all_plans = perf_df['plan'].dropna().unique().tolist()
with col3:
    selected_plans = st.multiselect("Plan", options=all_plans, default=all_plans)

# Apply filters
filtered_df = perf_df[
    (perf_df['fund_house'].isin(selected_houses)) &
    (perf_df['category'].isin(selected_categories)) &
    (perf_df['plan'].isin(selected_plans))
]

st.markdown("---")

# --- 3. SCATTER PLOT: RETURN VS RISK ---
st.subheader("Risk vs Return Analysis")
if not filtered_df.empty:
    fig_scatter = px.scatter(
        filtered_df, 
        x='return_3yr_pct', 
        y='std_dev_ann_pct', 
        size='aum_crore', 
        color='category',
        hover_name='scheme_name',
        title="Return (X) vs Risk (Y) | Bubble Size = AUM",
        labels={'return_3yr_pct': '3-Year Return (%)', 'std_dev_ann_pct': 'Annualized Risk (Std Dev %)'},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.warning("No data available for the selected filters. Please adjust the sidebar.")

st.markdown("---")

# --- 4. SORTABLE FUND SCORECARD TABLE ---
st.subheader("Sortable Fund Scorecard")
if not filtered_df.empty:
    scorecard_cols = [
        'amfi_code', 'scheme_name', 'category', 'return_1yr_pct', 
        'return_3yr_pct', 'return_5yr_pct', 'sharpe_ratio', 'expense_ratio_pct'
    ]
    st.dataframe(filtered_df[scorecard_cols], use_container_width=True, hide_index=True)

st.markdown("---")

# --- 5. LINE CHART: NAV VS BENCHMARK ---
st.subheader("NAV vs Benchmark Comparison")

if not filtered_df.empty:
    # Dropdown to select a single fund from the filtered list
    selected_fund_name = st.selectbox("Select a Fund to compare against its Benchmark:", options=filtered_df['scheme_name'].unique())
    selected_fund_row = filtered_df[filtered_df['scheme_name'] == selected_fund_name].iloc[0]
    selected_amfi = selected_fund_row['amfi_code']
    
    # Get benchmark name mapped to this fund
    fund_info_query = f"SELECT benchmark FROM dim_fund WHERE amfi_code = {selected_amfi}"
    fund_info_df = load_data(fund_info_query)
    
    if not fund_info_df.empty:
        benchmark_raw = fund_info_df.iloc[0]['benchmark']
        st.markdown(f"**Benchmark Assigned:** `{benchmark_raw}`")
        
        # Mapping to match fact_benchmark naming conventions
        benchmark_mapping = {
            "NIFTY 50 TRI": "NIFTY50",
            "NIFTY 100 TRI": "NIFTY100",
            "NIFTY Midcap 150 TRI": "NIFTY_MIDCAP150",
            "S&P BSE SmallCap TRI": "BSE_SMALLCAP",
            "NIFTY 500 TRI": "NIFTY500",
            "CRISIL Liquid Fund Index": "CRISIL_LIQUID",
            "CRISIL Dynamic Gilt Index": "CRISIL_GILT"
        }
        benchmark_mapped = benchmark_mapping.get(benchmark_raw, benchmark_raw.replace(" ", "").replace("TRI", ""))
        
        # Fetch historical NAV data for the selected fund
        nav_query = f"SELECT date, nav FROM fact_nav WHERE amfi_code = {selected_amfi} ORDER BY date"
        nav_df = load_data(nav_query)
        
        # Fetch historical Benchmark data
        bench_query = f"SELECT date, close_value FROM fact_benchmark WHERE index_name = '{benchmark_mapped}' ORDER BY date"
        bench_df = load_data(bench_query)
        
        if not nav_df.empty and not bench_df.empty:
            # Ensure dates are properly parsed for plotting
            nav_df['date'] = pd.to_datetime(nav_df['date'], dayfirst=True, format='mixed', errors='coerce')
            bench_df['date'] = pd.to_datetime(bench_df['date'], dayfirst=True, format='mixed', errors='coerce')
            
            # Drop invalid dates
            nav_df = nav_df.dropna(subset=['date'])
            bench_df = bench_df.dropna(subset=['date'])
            
            # Smooth data: Group by month and calculate average to mimic Power BI perfectly
            nav_monthly = nav_df.set_index('date').resample('ME').mean().reset_index().dropna()
            bench_monthly = bench_df.set_index('date').resample('ME').mean().reset_index().dropna()
            
            # Create a Dual-Axis Plotly Chart
            fig_nav = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_nav.add_trace(
                go.Scatter(x=nav_monthly['date'], y=nav_monthly['nav'], name="Fund NAV (Monthly Avg)", line=dict(color="#2E86C1", width=2)),
                secondary_y=False,
            )
            
            fig_nav.add_trace(
                go.Scatter(x=bench_monthly['date'], y=bench_monthly['close_value'], name=f"Benchmark ({benchmark_raw})", line=dict(color="#E74C3C", width=2)),
                secondary_y=True,
            )
            
            fig_nav.update_layout(title_text=f"{selected_fund_name} vs Benchmark Growth")
            fig_nav.update_yaxes(title_text="<b>NAV (₹)</b>", secondary_y=False, color="#2E86C1")
            fig_nav.update_yaxes(title_text="<b>Benchmark Value</b>", secondary_y=True, color="#E74C3C")
            
            st.plotly_chart(fig_nav, use_container_width=True)
        else:
            st.warning("Insufficient historical data to plot NAV vs Benchmark for this specific fund.")
    else:
         st.warning("Could not find a benchmark mapping for this fund in the database.")
