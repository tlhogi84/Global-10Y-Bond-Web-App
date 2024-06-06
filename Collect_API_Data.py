import requests
import pandas as pd
import io

# Load country codes
country_df = pd.read_csv("Country_Codes.csv")

# URLs to fetch data from
urls = [
    "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_FINMARK,4.0/.M.IRLT.PA.....",
    "https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0/.M.N.CPI.IX._T.N.",
    "https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0/NZL+AUS.Q.N.CPI.IX._T.N."
]

def fetch_and_filter_data(url, country_df):
    headers = {"Accept": "text/csv"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        csv_file = io.StringIO(response.text)
        df = pd.read_csv(csv_file)
        columns_to_keep = ["REF_AREA", "FREQ", "MEASURE", "UNIT_MEASURE", "TIME_PERIOD", "OBS_VALUE"]
        df_filtered = df[columns_to_keep].copy()
        
        # Rename columns
        df_filtered = df_filtered.rename(columns={
            "REF_AREA": "LOCATION",
            "FREQ": "FREQUENCY",
            "TIME_PERIOD": "TIME",
            "OBS_VALUE": "Value"
        })
        
        # Merge with country data to get country names
        df_merged = df_filtered.merge(country_df, left_on="LOCATION", right_on="LOCATION", how="left")
        
        # Reorder columns
        final_columns = ["LOCATION", "Country", "FREQUENCY", "MEASURE", "UNIT_MEASURE", "TIME", "Value"]
        df_final = df_merged[final_columns]
        
        return df_final
    else:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
        return None


# Fetch and process data for each URL
dfs = []
for i, url in enumerate(urls):
    df_final = fetch_and_filter_data(url, country_df)
    if df_final is not None:
        dfs.append(df_final)

# Save the first DataFrame separately
if len(dfs) > 0:
    dfs[0].to_csv("OECD_LTRATES_Data.csv", index=False)

# Combine the second and third DataFrames and save them
if len(dfs) > 1:
    combined_cpi_data = pd.concat(dfs[1:], ignore_index=True)
    combined_cpi_data.to_csv("OECD_CPI_Data.csv", index=False)