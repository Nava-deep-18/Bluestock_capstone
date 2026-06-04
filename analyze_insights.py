import pandas as pd
from pathlib import Path

data_dir = Path("c:/programming/bluestock_mf_capstone/data/processed")

# 1. AUM
aum_df = pd.read_csv(data_dir / "clean_aum_by_fund_house.csv")
aum_2025 = aum_df[pd.to_datetime(aum_df['date']).dt.year == 2025]
max_aum_2025 = aum_2025.groupby('fund_house')['aum_lakh_crore'].max().sort_values(ascending=False)
total_aum_2025 = max_aum_2025.sum()
sbi_aum = max_aum_2025.get('SBI Mutual Fund', 0)
print(f"1. AUM: SBI AUM in 2025: {sbi_aum}L Cr out of {total_aum_2025}L Cr ({(sbi_aum/total_aum_2025)*100:.1f}%)")

# 2. SIP
sip_df = pd.read_csv(data_dir / "clean_monthly_sip_inflows.csv")
sip_df['month'] = pd.to_datetime(sip_df['month'])
sip_df = sip_df.sort_values('month')
start_sip = sip_df.iloc[0]['sip_inflow_crore']
end_sip = sip_df.iloc[-1]['sip_inflow_crore']
print(f"2. SIP: Grew from {start_sip} Cr to {end_sip} Cr ({(end_sip/start_sip - 1)*100:.1f}% growth)")

# 3. Demographics & Geography
tx_df = pd.read_csv(data_dir / "clean_transactions.csv")
unique_investors = tx_df.drop_duplicates(subset=['investor_id'])
age_dist = unique_investors['age_group'].value_counts(normalize=True)*100
print(f"3. Demographics: Largest age group: {age_dist.index[0]} ({age_dist.iloc[0]:.1f}%)")

sip_tx = tx_df[tx_df['transaction_type'] == 'SIP']
tier_dist = sip_tx.groupby('city_tier')['amount_inr'].sum()
tier_pct = (tier_dist / tier_dist.sum()) * 100
print(f"4. Geography: T30 vs B30 SIP: T30={tier_pct.get('T30',0):.1f}%, B30={tier_pct.get('B30',0):.1f}%")

# 5. Folio
folio_df = pd.read_csv(data_dir / "clean_industry_folio_count.csv")
folio_df['month'] = pd.to_datetime(folio_df['month'])
folio_df = folio_df.sort_values('month')
start_folio = folio_df.iloc[0]['total_folios_crore']
end_folio = folio_df.iloc[-1]['total_folios_crore']
print(f"5. Folio: Grew from {start_folio} Cr to {end_folio} Cr")

# 6. Category Inflows
cat_df = pd.read_csv(data_dir / "clean_category_inflows.csv")
top_cat = cat_df.groupby('category')['net_inflow_crore'].sum().sort_values(ascending=False)
print(f"6. Categories: Top category by inflow is {top_cat.index[0]} with {top_cat.iloc[0]} Cr")

# 7. Sector Allocation
hold_df = pd.read_csv(data_dir / "clean_portfolio_holdings.csv")
fm_df = pd.read_csv(data_dir / "clean_fund_master.csv")
eq_funds = fm_df[fm_df['category'] == 'Equity']['amfi_code']
eq_holdings = hold_df[hold_df['amfi_code'].isin(eq_funds)]
sectors = eq_holdings.groupby('sector')['market_value_cr'].sum().sort_values(ascending=False)
total_eq = sectors.sum()
top_sector = sectors.index[0]
top_sec_pct = (sectors.iloc[0] / total_eq) * 100
print(f"7. Sectors: Top sector is {top_sector} taking {top_sec_pct:.1f}% of equity AUM")
