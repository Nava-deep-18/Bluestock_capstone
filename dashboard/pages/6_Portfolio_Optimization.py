"""
Module: 6_Portfolio_Optimization.py
Description: Component of the Bluestock Mutual Fund Analytics Capstone.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="Portfolio Optimization", layout="wide")

LOGO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logo.jpg'))
if os.path.exists(LOGO_PATH):
    st.logo(LOGO_PATH)

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

st.title("🎯 Markowitz Portfolio Optimization")
st.markdown("Select up to 5 Mutual Funds to find the mathematically optimal allocation (Efficient Frontier) that maximizes your returns while minimizing risk.")

# Fetch list of funds
funds_query = "SELECT DISTINCT scheme_name, amfi_code FROM dim_fund"
funds_df = load_data(funds_query)

if funds_df.empty:
    st.error("No fund data available.")
    st.stop()

# Default selection (first 5 funds just to populate the UI initially, or user selects)
default_funds = funds_df['scheme_name'].head(5).tolist()

selected_funds = st.multiselect(
    "Select up to 5 Mutual Funds to include in your portfolio", 
    options=funds_df['scheme_name'].tolist(),
    default=default_funds,
    max_selections=5
)

if len(selected_funds) < 2:
    st.warning("Please select at least 2 funds to run a portfolio optimization.")
    st.stop()

# 1. Fetch and Prepare Data
with st.spinner("Fetching data and calculating covariance..."):
    # Map names back to amfi_codes
    selected_amfi_codes = funds_df[funds_df['scheme_name'].isin(selected_funds)]['amfi_code'].tolist()
    amfi_to_name = dict(zip(funds_df['amfi_code'], funds_df['scheme_name']))
    
    # Query data for selected funds
    placeholders = ','.join(['?'] * len(selected_amfi_codes))
    query = f"SELECT date, amfi_code, nav FROM fact_nav WHERE amfi_code IN ({placeholders})"
    
    conn = sqlite3.connect(DB_PATH)
    raw_df = pd.read_sql(query, conn, params=selected_amfi_codes)
    conn.close()
    
    # Standardize dates
    raw_df['date'] = pd.to_datetime(raw_df['date'], errors='coerce')
    raw_df = raw_df.dropna(subset=['date', 'nav']).sort_values('date')
    raw_df['nav'] = pd.to_numeric(raw_df['nav'], errors='coerce')
    
    # Pivot to get a matrix where rows=date, columns=amfi_code, values=nav
    nav_pivot = raw_df.pivot(index='date', columns='amfi_code', values='nav')
    
    # Resample to business days and forward fill to handle different fund holidays
    nav_pivot = nav_pivot.resample('B').ffill().dropna()
    
    if nav_pivot.empty or len(nav_pivot) < 100:
        st.error("Not enough overlapping historical data between these selected funds to run a correlation.")
        st.stop()
        
    # Calculate daily returns
    returns_df = nav_pivot.pct_change().dropna()
    
    # Rename columns to Scheme Names for readability
    returns_df.columns = [amfi_to_name.get(col, col) for col in returns_df.columns]
    
    # 2. Covariance and Returns Math
    TRADING_DAYS = 252
    RISK_FREE_RATE = 0.07 # 7.0% Indian Risk-Free Rate
    
    # Annualized Returns
    mean_returns = returns_df.mean() * TRADING_DAYS
    
    # Annualized Covariance Matrix
    cov_matrix = returns_df.cov() * TRADING_DAYS

# 3. The Simulation Engine
st.markdown("---")
NUM_PORTFOLIOS = 10000

with st.spinner("Simulating 10,000 Portfolio Combinations..."):
    num_funds = len(selected_funds)
    
    # Generate random weights (Dirichlet distribution ensures they sum to 1)
    weights = np.random.dirichlet(np.ones(num_funds), size=NUM_PORTFOLIOS)
    
    # Calculate Portfolio Returns
    # Dot product of weights and mean returns
    port_returns = np.dot(weights, mean_returns)
    
    # Calculate Portfolio Volatility (Risk)
    # sqrt( w.T * Cov * w ) for each row
    port_volatility = np.zeros(NUM_PORTFOLIOS)
    for i in range(NUM_PORTFOLIOS):
        port_volatility[i] = np.sqrt(np.dot(weights[i].T, np.dot(cov_matrix, weights[i])))
        
    # Calculate Sharpe Ratio
    sharpe_ratios = (port_returns - RISK_FREE_RATE) / port_volatility
    
    # Create a DataFrame of the results
    port_results = pd.DataFrame({
        'Return': port_returns,
        'Volatility': port_volatility,
        'Sharpe': sharpe_ratios
    })
    
    # Add weights to the DataFrame
    for i, fund_name in enumerate(returns_df.columns):
        port_results[fund_name + ' Weight'] = weights[:, i]

# Extract Optimal Portfolios
max_sharpe_idx = port_results['Sharpe'].idxmax()
max_sharpe_port = port_results.loc[max_sharpe_idx]

min_vol_idx = port_results['Volatility'].idxmin()
min_vol_port = port_results.loc[min_vol_idx]

# 4. Visualization (Efficient Frontier)
fig = go.Figure()

# Plot all 10,000 portfolios
fig.add_trace(go.Scatter(
    x=port_results['Volatility'],
    y=port_results['Return'],
    mode='markers',
    marker=dict(
        color=port_results['Sharpe'],
        colorscale='Viridis',
        size=4,
        colorbar=dict(title="Sharpe Ratio"),
        showscale=True
    ),
    name='Simulated Portfolios',
    hovertext=[f"Return: {r*100:.1f}%<br>Risk: {v*100:.1f}%<br>Sharpe: {s:.2f}" 
               for r, v, s in zip(port_results['Return'], port_results['Volatility'], port_results['Sharpe'])],
    hoverinfo='text'
))

# Highlight Maximum Sharpe Portfolio
fig.add_trace(go.Scatter(
    x=[max_sharpe_port['Volatility']],
    y=[max_sharpe_port['Return']],
    mode='markers',
    marker=dict(color='gold', size=15, symbol='star', line=dict(color='white', width=1)),
    name='🏆 Maximum Sharpe Ratio'
))

# Highlight Minimum Volatility Portfolio
fig.add_trace(go.Scatter(
    x=[min_vol_port['Volatility']],
    y=[min_vol_port['Return']],
    mode='markers',
    marker=dict(color='red', size=15, symbol='star', line=dict(color='white', width=1)),
    name='🛡️ Minimum Volatility'
))

fig.update_layout(
    title="Markowitz Efficient Frontier (10,000 Simulations)",
    xaxis_title="Risk (Annualized Volatility)",
    yaxis_title="Expected Annual Return",
    template="plotly_dark",
    height=600,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# 5. Output Optimal Weights
st.markdown("### 🏆 Optimal Portfolio Breakdown (Max Sharpe Ratio)")
st.markdown("This exact combination provides the highest possible return for every unit of risk you take.")

# Create columns for metrics
col1, col2, col3 = st.columns(3)
col1.metric("Expected Annual Return", f"{max_sharpe_port['Return']*100:.2f}%")
col2.metric("Expected Annual Risk", f"{max_sharpe_port['Volatility']*100:.2f}%")
col3.metric("Sharpe Ratio", f"{max_sharpe_port['Sharpe']:.2f}")

# Plot weights as a Donut Chart
weight_cols = [col for col in max_sharpe_port.index if 'Weight' in col]
weights_values = max_sharpe_port[weight_cols].values * 100
fund_names = [col.replace(' Weight', '') for col in weight_cols]

weights_df = pd.DataFrame({
    'Fund': fund_names,
    'Allocation (%)': weights_values
})
# Filter out tiny weights (< 1%) for a cleaner chart
weights_df = weights_df[weights_df['Allocation (%)'] > 1.0]

fig_pie = px.pie(
    weights_df, 
    values='Allocation (%)', 
    names='Fund', 
    hole=0.4,
    title="Optimal Capital Allocation",
    template="plotly_dark"
)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')

st.plotly_chart(fig_pie, use_container_width=True)
