# Data Dictionary: Bluestock Mutual Fund Analytics Database

This document provides a comprehensive overview of the SQLite database schema (`bluestock_mf.db`) used for this project. The database follows a classic star schema architecture.

## 1. dim_fund (Dimension Table)
*Source: `01_fund_master.csv`* | *Rows: 40*
Stores static master data about each mutual fund scheme.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `amfi_code` | TEXT (PK) | AMFI unique scheme code (e.g. 125497) |
| `fund_house` | TEXT | AMC name (e.g. SBI Mutual Fund) |
| `scheme_name` | TEXT | Full official AMFI scheme name |
| `category` | TEXT | Equity / Debt / Hybrid |
| `sub_category` | TEXT | Large Cap / Mid Cap / Small Cap / Liquid / etc. |
| `plan` | TEXT | Regular or Direct |
| `launch_date` | TEXT | Fund launch date |
| `benchmark` | TEXT | Official benchmark index |
| `expense_ratio_pct` | REAL | Annual expense ratio in % |
| `exit_load_pct` | REAL | Exit load % |
| `min_sip_amount` | INTEGER | Minimum SIP investment allowed |
| `min_lumpsum_amount` | INTEGER | Minimum Lumpsum investment allowed |
| `fund_manager` | TEXT | Name of primary fund manager |
| `risk_category` | TEXT | SEBI risk category (Low / Moderate / High) |
| `sebi_category_code` | TEXT | Internal code |

## 2. fact_nav (Fact Table)
*Source: `02_nav_history.csv`* | *Rows: ~64,320*
Stores daily historical NAV data for the schemes.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `amfi_code` | TEXT (FK) | Foreign key mapping to dim_fund |
| `date` | TEXT | NAV date (business days + forward-filled weekends) |
| `nav` | REAL | Net Asset Value in INR |

## 3. fact_transactions (Fact Table)
*Source: `08_investor_transactions.csv`* | *Rows: ~32,778*
Stores transactional activities by simulated demographic profiles.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `investor_id` | TEXT | Unique investor identifier |
| `transaction_date` | TEXT | Date of transaction |
| `amfi_code` | TEXT (FK) | Fund in which transaction occurred |
| `transaction_type` | TEXT | SIP / Lumpsum / Redemption |
| `amount_inr` | INTEGER | Transaction amount in INR |
| `state` | TEXT | Investor's state |
| `city` | TEXT | Investor's city |
| `city_tier` | TEXT | T30 (Top 30 cities) or B30 per AMFI classification |
| `age_group` | TEXT | Age bracket |
| `gender` | TEXT | Male / Female |
| `annual_income_lakh` | REAL | Annual income in Lakh INR |
| `payment_mode` | TEXT | UPI / Net Banking / Mandate / Cheque |
| `kyc_status` | TEXT | Verified / Pending |

## 4. fact_performance (Fact Table)
*Source: `07_scheme_performance.csv`* | *Rows: 40*
Stores calculated point-in-time performance and risk metrics.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `amfi_code` | TEXT (FK) | Foreign key mapping to dim_fund |
| `scheme_name` | TEXT | Name of scheme |
| `return_1yr_pct` | REAL | 1-year absolute return % |
| `return_3yr_pct` | REAL | 3-year CAGR % |
| `return_5yr_pct` | REAL | 5-year CAGR % |
| `benchmark_3yr_pct` | REAL | Benchmark index 3yr CAGR |
| `alpha` | REAL | Return above benchmark |
| `beta` | REAL | Sensitivity to market |
| `sharpe_ratio` | REAL | Risk-adjusted return |
| `sortino_ratio` | REAL | Downside risk-adjusted return |
| `std_dev_ann_pct` | REAL | Annualised standard deviation |
| `max_drawdown_pct` | REAL | Worst peak-to-trough decline |
| `aum_crore` | REAL | Assets Under Management in Cr |
| `expense_ratio_pct` | REAL | Expense ratio |
| `morningstar_rating` | INTEGER | 1-5 star rating |
| `risk_grade` | TEXT | Risk classification |
| `has_negative_sharpe` | INTEGER | Boolean flag (1=True, 0=False) |

## 5. fact_sip_industry (Fact Table)
*Source: `04_monthly_sip_inflows.csv`* | *Rows: 48*
Stores monthly macro SIP data for the Indian mutual fund industry.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `month` | TEXT | YYYY-MM format |
| `sip_inflow_crore` | REAL | Total SIP inflows in Rs. crore |
| `active_sip_accounts_crore` | REAL | Active contributing accounts |
| `new_sip_accounts_lakh` | REAL | New accounts registered |
| `sip_aum_lakh_crore` | REAL | Total SIP AUM |
| `yoy_growth_pct` | REAL | Year-over-Year growth % (Null for first year) |

## 6. fact_portfolio (Fact Table)
*Source: `09_portfolio_holdings.csv`* | *Rows: 322*
Stores equity holdings (top stocks) for mutual funds.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `amfi_code` | TEXT (FK) | Foreign key |
| `stock_symbol` | TEXT | Ticker symbol |
| `stock_name` | TEXT | Company name |
| `sector` | TEXT | Industry sector |
| `weight_pct` | REAL | Percentage of portfolio allocated |
| `market_value_cr` | REAL | Market value held in Crores |
| `current_price_inr` | REAL | Current stock price |
| `portfolio_date` | TEXT | Date of portfolio disclosure |

## 7. fact_aum (Fact Table)
*Source: `03_aum_by_fund_house.csv`* | *Rows: 90*
Stores aggregate AUM split by Fund House over time.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `date` | TEXT | Date of report |
| `fund_house` | TEXT | AMC name |
| `aum_lakh_crore` | REAL | AUM in Lakh Crores |
| `aum_crore` | INTEGER | AUM in Crores |
| `num_schemes` | INTEGER | Number of active schemes |

## 8. fact_benchmark (Fact Table)
*Source: `10_benchmark_indices.csv`* | *Rows: ~8,050*
Stores daily closing values for major stock market indices.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `date` | TEXT | Trading date |
| `index_name` | TEXT | Name of index (e.g. Nifty 50) |
| `close_value` | REAL | Closing points value |

## 9. fact_category_inflows (Fact Table)
*Source: `05_category_inflows.csv`* | *Rows: 144*
Stores net inflows separated by mutual fund category.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `month` | TEXT | YYYY-MM |
| `category` | TEXT | Fund category (Large Cap, Liquid, etc.) |
| `net_inflow_crore` | REAL | Net capital inflow in Crores |

## 10. fact_folio_count (Fact Table)
*Source: `06_industry_folio_count.csv`* | *Rows: 21*
Stores total active folios separated by asset class.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `month` | TEXT | YYYY-MM |
| `total_folios_crore` | REAL | Total folios |
| `equity_folios_crore` | REAL | Folios in equity funds |
| `debt_folios_crore` | REAL | Folios in debt funds |
| `hybrid_folios_crore` | REAL | Folios in hybrid funds |
| `others_folios_crore` | REAL | Folios in other funds |
