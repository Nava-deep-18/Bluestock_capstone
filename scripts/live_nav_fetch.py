import requests
import pandas as pd
import os
import time

def fetch_and_update_nav(amfi_codes, raw_dir):
    print("\n[STEP 1] Fetching Live Data from mfapi.in...")
    history_file = os.path.join(raw_dir, '02_nav_history.csv')
    
    # Load existing static history
    if os.path.exists(history_file):
        existing_df = pd.read_csv(history_file)
        initial_rows = len(existing_df)
        print(f"Loaded existing history with {initial_rows} rows.")
    else:
        existing_df = pd.DataFrame(columns=['amfi_code', 'date', 'nav'])
        initial_rows = 0

    new_data_frames = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for code in amfi_codes:
        print(f" -> Fetching NAV for AMFI Code: {code}")
        url = f"https://api.mfapi.in/mf/{code}"
        try:
            response = requests.get(url, headers=headers, timeout=25)
            if response.status_code == 200:
                data = response.json()
                nav_data = data.get('data', [])
                if nav_data:
                    df = pd.DataFrame(nav_data)
                    df['amfi_code'] = int(code)  # Ensure type matches existing data
                    df = df[['amfi_code', 'date', 'nav']]
                    new_data_frames.append(df)
            else:
                print(f"    Failed API call for {code}. Status: {response.status_code}")
        except Exception as e:
            print(f"    Error for {code}: {e}")
        time.sleep(1) # Be polite to the API
        
    if new_data_frames:
        # Combine newly fetched data
        new_df = pd.concat(new_data_frames, ignore_index=True)
        
        # Merge with existing historical data
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # Standardize dates to strictly identify duplicates
        combined_df['date_parsed'] = pd.to_datetime(combined_df['date'], dayfirst=True, format="mixed")
        
        # Sort so we keep the absolute latest entry if there are overlaps
        combined_df = combined_df.sort_values(by=['amfi_code', 'date_parsed'])
        
        # Drop duplicates (this ensures we only add NEW days that didn't exist before)
        combined_df = combined_df.drop_duplicates(subset=['amfi_code', 'date_parsed'], keep='last')
        
        # Drop temporary parsing column
        combined_df = combined_df.drop(columns=['date_parsed'])
        
        # Overwrite the raw CSV file with the beautifully merged data
        combined_df.to_csv(history_file, index=False)
        final_rows = len(combined_df)
        print(f"[SUCCESS] Updated 02_nav_history.csv! Added {final_rows - initial_rows} new rows of live data.")
    else:
        print("No new data was fetched.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    raw_dir = os.path.join(project_root, "data", "raw")
    
    # The 5 funds required by the project specifications
    target_funds = ["119551", "120503", "118632", "119092", "120841"]
    
    fetch_and_update_nav(target_funds, raw_dir)
