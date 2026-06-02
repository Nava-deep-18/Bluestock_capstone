import requests
import pandas as pd
import os
import time

def fetch_and_save_nav(amfi_code, output_dir, retries=3):
    print(f"--- Fetching Live NAV for {amfi_code} ---")
    url = f"https://api.mfapi.in/mf/{amfi_code}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=25)
            if response.status_code == 200:
                data = response.json()
                nav_data = data.get('data', [])
                if nav_data:
                    df = pd.DataFrame(nav_data)
                    df['amfi_code'] = amfi_code
                    df = df[['amfi_code', 'date', 'nav']]
                    output_path = os.path.join(output_dir, f"{amfi_code}_raw_nav.csv")
                    df.to_csv(output_path, index=False)
                    print(f"Successfully saved {len(df)} rows to {output_path}")
                    return # Success
                else:
                    print(f"No NAV data found for {amfi_code}.")
                    return
            else:
                print(f"Failed to fetch data for {amfi_code}. Status code: {response.status_code}")
                break
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1} failed for {amfi_code}: {e}")
            time.sleep(3) # Wait before retry

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, "data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    
    # Retry fetching the last one that timed out
    fetch_and_save_nav("120841", output_dir)
    print("\nAll NAV fetching completed!")
