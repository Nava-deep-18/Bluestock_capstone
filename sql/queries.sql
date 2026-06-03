-- ==========================================
-- Mutual Fund Analytics SQL Queries
-- ==========================================

-- 1. Top 5 funds by AUM
SELECT scheme_name, fund_house, aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;

/* --- RESULTS ---
                                          scheme_name        fund_house  aum_crore
Mirae Asset Emerging Bluechip Fund - Regular - Growth    Mirae Asset MF      49046
        Kotak Emerging Equity Fund - Regular - Growth Kotak Mahindra MF      47469
       Nippon India Small Cap Fund - Regular - Growth   Nippon India MF      43630
           DSP Top 100 Equity Fund - Regular - Growth   DSP Mutual Fund      41828
                  UTI Mid Cap Fund - Regular - Growth   UTI Mutual Fund      41728
------------------ */

-- 2. Average NAV per month (overall trend)
SELECT strftime('%Y-%m', date) AS month, ROUND(AVG(nav), 2) as avg_nav
FROM fact_nav
GROUP BY month
ORDER BY month DESC
LIMIT 5;

/* --- RESULTS ---
  month  avg_nav
2026-05   356.99
2026-04   355.03
2026-03   347.21
2026-02   342.03
2026-01   337.07
------------------ */

-- 3. SIP inflow YoY growth (Most recent 5 months)
SELECT month, sip_inflow_crore, yoy_growth_pct
FROM fact_sip_industry
WHERE yoy_growth_pct IS NOT NULL
ORDER BY month DESC
LIMIT 5;

/* --- RESULTS ---
  month  sip_inflow_crore  yoy_growth_pct
2025-12             31002           17.17
2025-11             30200           19.27
2025-10             29529           16.61
2025-09             29361           19.80
2025-08             28265           20.04
------------------ */

-- 4. Transactions by state (Top 5 by total amount)
SELECT state, COUNT(*) as total_transactions, SUM(amount_inr) as total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC
LIMIT 5;

/* --- RESULTS ---
         state  total_transactions  total_amount
        Punjab                2965     315780459
    Tamil Nadu                2806     315177237
Madhya Pradesh                2931     308312493
     Rajasthan                2577     298645822
       Gujarat                2780     298358940
------------------ */

-- 5. Funds with expense_ratio < 1% (Lowest 5)
SELECT scheme_name, expense_ratio_pct, category
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC
LIMIT 5;

/* --- RESULTS ---
                                         scheme_name  expense_ratio_pct category
Nippon India Gilt Securities Fund - Regular - Growth               0.55     Debt
        HDFC Short Term Debt Fund - Regular - Growth               0.56     Debt
                Kotak Liquid Fund - Regular - Growth               0.60     Debt
            SBI Bluechip Fund - Direct Plan - Growth               0.66   Equity
           SBI Small Cap Fund - Direct Plan - Growth               0.72   Equity
------------------ */

-- 6. Total transaction volume by type
SELECT transaction_type, COUNT(*) as tx_count, ROUND(SUM(amount_inr)/100000.0, 2) as amount_lakhs
FROM fact_transactions
GROUP BY transaction_type
ORDER BY tx_count DESC;

/* --- RESULTS ---
transaction_type  tx_count  amount_lakhs
             SIP     19716       2172.33
         Lumpsum      8095      20598.21
      Redemption      4967      12445.25
------------------ */

-- 7. Top 5 equity sectors by average weight
SELECT sector, ROUND(AVG(weight_pct), 2) as avg_weight
FROM fact_portfolio
GROUP BY sector
ORDER BY avg_weight DESC
LIMIT 5;

/* --- RESULTS ---
        sector  avg_weight
Consumer Goods       14.18
   Diversified       12.09
            IT       11.39
     Utilities       11.06
          FMCG       10.91
------------------ */

-- 8. Largest Fund Houses by Total AUM (from AUM fact table)
SELECT fund_house, SUM(aum_crore) as total_aum
FROM fact_aum
GROUP BY fund_house
ORDER BY total_aum DESC
LIMIT 5;

/* --- RESULTS ---
         fund_house  total_aum
    SBI Mutual Fund    8491000
ICICI Prudential MF    6293000
   HDFC Mutual Fund    5732000
    Nippon India MF    3909000
  Kotak Mahindra MF    3502000
------------------ */

-- 9. Count of funds per category
SELECT category, COUNT(*) as num_funds
FROM dim_fund
GROUP BY category
ORDER BY num_funds DESC;

/* --- RESULTS ---
category  num_funds
  Equity         34
    Debt          6
------------------ */

-- 10. Average 3-year return per risk category
SELECT d.risk_category, ROUND(AVG(p.return_3yr_pct), 2) as avg_3yr_return
FROM dim_fund d
JOIN fact_performance p ON d.amfi_code = p.amfi_code
GROUP BY d.risk_category
ORDER BY avg_3yr_return DESC;

/* --- RESULTS ---
  risk_category  avg_3yr_return
      Very High           21.69
           High           16.21
Moderately High           15.08
       Moderate           12.85
            Low            6.29
------------------ */

