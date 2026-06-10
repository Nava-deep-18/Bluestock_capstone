import streamlit as st
import os

# Configure the main application page
st.set_page_config(
    page_title="Bluestock MF Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOGO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logo.jpg'))
if os.path.exists(LOGO_PATH):
    st.logo(LOGO_PATH)

# Landing page welcome message
st.title("📈 Bluestock Mutual Fund Analytics")
st.markdown("""
Welcome to the interactive mutual fund dashboard! 

This dashboard connects directly to the live SQLite database (`bluestock_mf.db`) to provide real-time analytics.
Please select a page from the sidebar menu to explore different analytics:

* **1. Industry Overview:** Macro-level KPIs and AUM trends.
* **2. Fund Performance:** Deep-dive into specific mutual funds and risk metrics.
* **3. Investor Analytics:** Demographic breakdowns and transaction patterns.
* **4. SIP & Trends:** Market cashflows and benchmark comparisons.
""")
