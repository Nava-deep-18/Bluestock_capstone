import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

st.set_page_config(page_title="Investor Analytics", layout="wide")

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

st.title("👥 Investor Analytics")
st.markdown("Analyze transaction patterns, demographics, and geographic distributions.")

# --- 1. FETCH DATA ---
trans_query = "SELECT * FROM fact_transactions"
df = load_data(trans_query)

if df.empty:
    st.error("No transaction data found in the database.")
    st.stop()

# --- 2. TOP SLICERS (FILTERS) ---
st.markdown("### Filter Options")
col1, col2, col3 = st.columns(3)

with col1:
    all_states = df['state'].dropna().unique().tolist()
    selected_states = st.multiselect("State", options=all_states, default=all_states)

with col2:
    all_ages = df['age_group'].dropna().unique().tolist()
    selected_ages = st.multiselect("Age Group", options=all_ages, default=all_ages)

with col3:
    all_tiers = df['city_tier'].dropna().unique().tolist()
    selected_tiers = st.multiselect("City Tier", options=all_tiers, default=all_tiers)

# Apply filters
filtered_df = df[
    (df['state'].isin(selected_states)) &
    (df['age_group'].isin(selected_ages)) &
    (df['city_tier'].isin(selected_tiers))
]

st.markdown("---")

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# --- 3. CHARTS ---
row1_col1, row1_col2 = st.columns(2)

# Chart 1: Transaction Amount by State (Bar Chart replacing Map for simplicity)
with row1_col1:
    st.subheader("Transaction Amount by State")
    state_df = filtered_df.groupby('state')['amount_inr'].sum().reset_index()
    fig_state = px.bar(
        state_df, 
        x='state', 
        y='amount_inr', 
        title="Total Transaction Amount per State",
        color='amount_inr',
        color_continuous_scale="Blues"
    )
    fig_state.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_state, use_container_width=True)

# Chart 2: SIP vs Lumpsum vs Redemption Split (Donut Chart)
with row1_col2:
    st.subheader("Transaction Type Split")
    type_df = filtered_df.groupby('transaction_type')['amount_inr'].sum().reset_index()
    fig_donut = px.pie(
        type_df, 
        values='amount_inr', 
        names='transaction_type', 
        hole=0.4,
        title="SIP vs Lumpsum vs Redemption",
        color_discrete_sequence=['#2E86C1', '#28B463', '#E74C3C']
    )
    st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("---")

row2_col1, row2_col2 = st.columns(2)

# Chart 3: Age Group vs Avg SIP Amount (Bar Chart)
with row2_col1:
    st.subheader("Avg SIP Amount by Age Group")
    sip_only = filtered_df[filtered_df['transaction_type'] == 'SIP']
    if not sip_only.empty:
        age_sip_df = sip_only.groupby('age_group')['amount_inr'].mean().reset_index()
        fig_age = px.bar(
            age_sip_df, 
            x='age_group', 
            y='amount_inr',
            title="Average SIP Ticket Size across Demographics",
            color_discrete_sequence=['#8E44AD']
        )
        st.plotly_chart(fig_age, use_container_width=True)
    else:
        st.info("No SIP transactions found for the selected filters.")

# Chart 4: Monthly Transaction Volume (Line Chart)
with row2_col2:
    st.subheader("Monthly Transaction Volume")
    # Convert dates and group by month
    filtered_df['transaction_date'] = pd.to_datetime(filtered_df['transaction_date'], dayfirst=True, format='mixed', errors='coerce')
    valid_dates = filtered_df.dropna(subset=['transaction_date'])
    
    if not valid_dates.empty:
        # Group by exact date to get daily count of unique investors
        daily_vol = valid_dates.groupby('transaction_date')['investor_id'].nunique().reset_index(name='unique_investors')
        daily_vol = daily_vol.sort_values('transaction_date')
        
        fig_line = px.line(
            daily_vol, 
            x='transaction_date', 
            y='unique_investors',
            title="Daily Active Investors (Unique IDs)",
            labels={'unique_investors': 'Unique Investors'},
            color_discrete_sequence=['#F39C12']
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No valid transaction dates to plot volume.")
