import pandas as pd
from pathlib import Path

def recommend_funds(risk_appetite):
    print(f"Generating recommendations for risk appetite: {risk_appetite.upper()}...")
    
    # Define dynamic paths
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / 'data' / 'processed'
    
    # 1. Load Data
    try:
        funds = pd.read_csv(data_dir / 'clean_fund_master.csv')
        sharpe = pd.read_csv(data_dir / 'sharpe_values.csv')
    except FileNotFoundError:
        print("Error: Could not find the necessary CSV files in data/processed/")
        return
        
    # Find the exact name of the Sharpe column dynamically (usually 'sharpe_ratio' or 'Sharpe_Ratio')
    sharpe_col = [col for col in sharpe.columns if 'sharpe' in col.lower()][0]
    
    # Merge the funds with their Sharpe ratios
    df = pd.merge(funds, sharpe, on='amfi_code')
    
    # 2. Determine Risk Grade
    # If the database has a specific risk column, use it. Otherwise, accurately map the standard Categories
    if 'risk_grade' in df.columns:
        risk_col = 'risk_grade'
    elif 'risk_level' in df.columns:
        risk_col = 'risk_level'
    else:
        # Fallback mapping based on Category and Sub-category
        def map_risk(row):
            cat = str(row['category']).lower()
            sub = str(row['sub_category']).lower()
            
            if 'debt' in cat:
                return 'Low'
            elif 'equity' in cat:
                # Large Cap and Index funds are generally considered Moderate risk
                if 'large' in sub or 'index' in sub or 'etf' in sub:
                    return 'Moderate'
                # Small Cap, Mid Cap, Flexi Cap are High risk
                else:
                    return 'High'
            return 'Moderate'
            
        df['mapped_risk'] = df.apply(map_risk, axis=1)
        risk_col = 'mapped_risk'
        
    # 3. Filter by Risk Appetite
    target_risk = risk_appetite.lower()
    
    if risk_col == 'mapped_risk':
        filtered_df = df[df[risk_col].str.lower() == target_risk]
    else:
        # If using real DB risk_levels, use 'contains' to catch things like "Low to Moderate" if they type "Low"
        filtered_df = df[df[risk_col].str.lower().str.contains(target_risk, na=False)]
        
    if filtered_df.empty:
        print(f"No funds found matching risk profile: {risk_appetite}")
        return
        
    # 4. Sort by Sharpe Ratio (Highest is best)
    top_3 = filtered_df.sort_values(by=sharpe_col, ascending=False).head(3)
    
    # 5. Print Recommendation Table
    print(f"\n--- TOP 3 RECOMMENDED FUNDS ({risk_appetite.upper()} RISK) ---")
    
    # Format the output beautifully for the terminal
    output = top_3[['scheme_name', 'category', sharpe_col]].copy()
    output.rename(columns={
        'scheme_name': 'Fund Name', 
        'category': 'Category',
        sharpe_col: 'Sharpe Ratio'
    }, inplace=True)
    
    output['Sharpe Ratio'] = output['Sharpe Ratio'].round(2)
    output.index = range(1, len(output) + 1) # Make row numbers 1, 2, 3
    
    print(output.to_string())
    print("-" * 75 + "\n")

if __name__ == "__main__":
    print("===========================================================================")
    print("            BLUESTOCK ASSET MANAGEMENT - FUND RECOMMENDER")
    print("===========================================================================\n")
    
    # Run the recommender for all three risk profiles to prove it works perfectly
    recommend_funds("Low")
    recommend_funds("Moderate")
    recommend_funds("High")
