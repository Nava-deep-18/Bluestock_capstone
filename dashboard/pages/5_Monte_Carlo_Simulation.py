"""
Module: 5_Monte_Carlo_Simulation.py
Description: Component of the Bluestock Mutual Fund Analytics Capstone.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
import os
import datetime

st.set_page_config(page_title="Monte Carlo Simulation", layout="wide")

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

st.title("🎲 Monte Carlo NAV Projection")
st.markdown("Project future Mutual Fund NAV growth over the next 5 years using thousands of simulated parallel universes based on historical volatility.")

# Fetch list of funds
funds_query = "SELECT DISTINCT scheme_name, amfi_code FROM dim_fund"
funds_df = load_data(funds_query)

if funds_df.empty:
    st.error("No fund data available.")
    st.stop()

selected_fund = st.selectbox("Select a Mutual Fund to Simulate", options=funds_df['scheme_name'].tolist())
amfi_code = funds_df[funds_df['scheme_name'] == selected_fund].iloc[0]['amfi_code']

# Fetch historical NAV for the selected fund
nav_query = f"SELECT date, nav FROM fact_nav WHERE amfi_code = '{amfi_code}' ORDER BY date ASC"
nav_df = load_data(nav_query)

if nav_df.empty or len(nav_df) < 50:
    st.warning("Not enough historical data to run a reliable Monte Carlo simulation for this fund.")
    st.stop()

# --- DATA PREP & MATH ---
nav_df['date'] = pd.to_datetime(nav_df['date'], errors='coerce')
nav_df = nav_df.dropna(subset=['date', 'nav']).sort_values('date')
nav_df['nav'] = pd.to_numeric(nav_df['nav'], errors='coerce')

# Resample to strictly business days and forward-fill missing values
# This prevents multi-day gaps from looking like massive 1-day volatility spikes
nav_df = nav_df.set_index('date').resample('B').ffill().reset_index()

# Calculate daily percentage returns
nav_df['daily_return'] = nav_df['nav'].pct_change()

# CRISIS AVERTED: Clip impossible data artifacts. 
# Some funds in the raw API data have corrupt "jumps" (e.g. NAV jumping from 50 to 120 in one day). 
# We cap daily returns at a maximum of ±3% to ensure realistic mutual fund volatility.
nav_df['daily_return'] = nav_df['daily_return'].clip(lower=-0.03, upper=0.03)

# Historical Mean and Std Dev
mu = nav_df['daily_return'].mean()
sigma = nav_df['daily_return'].std()

latest_date = nav_df['date'].iloc[-1]
latest_nav = nav_df['nav'].iloc[-1]

st.markdown("### Historical Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Current NAV", f"₹{latest_nav:.2f}")
col2.metric("Daily Volatility (Std Dev)", f"{sigma*100:.3f}%")
col3.metric("Avg Daily Return", f"{mu*100:.3f}%")

st.markdown("---")

# --- MONTE CARLO ENGINE ---
NUM_SIMULATIONS = 500
YEARS = 5
TRADING_DAYS_PER_YEAR = 252
TIME_HORIZON = YEARS * TRADING_DAYS_PER_YEAR

with st.spinner("Running 500 parallel universe simulations..."):
    # Generate random daily returns for all simulations at once (Normal Distribution)
    # Shape: (TIME_HORIZON, NUM_SIMULATIONS)
    simulated_daily_returns = np.random.normal(mu, sigma, (TIME_HORIZON, NUM_SIMULATIONS))
    
    # Calculate price paths using cumulative product
    # Price = Last_Price * (1 + return_day1) * (1 + return_day2) ...
    price_paths = np.zeros_like(simulated_daily_returns)
    price_paths[0] = latest_nav * (1 + simulated_daily_returns[0])
    
    for t in range(1, TIME_HORIZON):
        price_paths[t] = price_paths[t-1] * (1 + simulated_daily_returns[t])
    
    # Generate future dates
    future_dates = [latest_date + datetime.timedelta(days=i) for i in range(1, TIME_HORIZON + 1)]
    
    # Calculate Percentiles (Uncertainty Bands) at each time step
    p5 = np.percentile(price_paths, 5, axis=1)   # Worst Case (Bottom 5%)
    p50 = np.percentile(price_paths, 50, axis=1) # Expected (Median)
    p95 = np.percentile(price_paths, 95, axis=1) # Best Case (Top 5%)

# --- VISUALIZATION ---
st.subheader("5-Year NAV Projection with Uncertainty Bands")

fig = go.Figure()

# 1. Plot Historical NAV (Last 2 years for context)
historical_plot = nav_df.tail(TRADING_DAYS_PER_YEAR * 2)
fig.add_trace(go.Scatter(
    x=historical_plot['date'], 
    y=historical_plot['nav'], 
    mode='lines', 
    name='Historical NAV',
    line=dict(color='white', width=2)
))

# 2. Plot Worst Case (Lower Band)
fig.add_trace(go.Scatter(
    x=future_dates, 
    y=p5, 
    mode='lines', 
    name='Worst Case (5th Percentile)',
    line=dict(color='rgba(231, 76, 60, 0)'), # Invisible line for filling
    showlegend=False
))

# 3. Plot Best Case (Upper Band) + Fill to Worst Case
fig.add_trace(go.Scatter(
    x=future_dates, 
    y=p95, 
    mode='lines', 
    name='Uncertainty Band (5% - 95%)',
    fill='tonexty', # Fill to the previous trace (Worst Case)
    fillcolor='rgba(52, 152, 219, 0.2)', # Transparent blue
    line=dict(color='rgba(52, 152, 219, 0)'),
    showlegend=True
))

# 4. Plot Expected (Median) Line
fig.add_trace(go.Scatter(
    x=future_dates, 
    y=p50, 
    mode='lines', 
    name='Expected Projection (Median)',
    line=dict(color='#3498DB', width=3)
))

# Formatting
fig.update_layout(
    title=f"Monte Carlo Simulation for {selected_fund}",
    xaxis_title="Date",
    yaxis_title="Net Asset Value (NAV) in ₹",
    hovermode="x unified",
    template="plotly_dark",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# Final 5-Year Metrics
st.markdown("### Projection Results (5 Years from now)")
res_col1, res_col2, res_col3 = st.columns(3)
res_col1.metric("Worst Case NAV", f"₹{p5[-1]:.2f}")
res_col2.metric("Expected NAV", f"₹{p50[-1]:.2f}")
res_col3.metric("Best Case NAV", f"₹{p95[-1]:.2f}")
