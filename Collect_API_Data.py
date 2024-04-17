import pandas as pd

def get_from_oecd(sdmx_query):
    return pd.read_csv(
        f"https://stats.oecd.org/SDMX-JSON/data/{sdmx_query}?contentType=csv",
        dtype={'Reference Period Code': str, 'Reference Period': str},
        low_memory=False
    )

sdmx_query_CPI = "PRICES_CPI/all"
df_CPI = get_from_oecd(sdmx_query_CPI)

sdmx_query_LTRATES = "MEI_FIN/all"
df_LTRATES = get_from_oecd(sdmx_query_LTRATES)

df_CPI_filtered = df_CPI[(df_CPI['MEASURE'] == 'IXOB') & ((df_CPI['FREQUENCY'] == 'M') | (df_CPI['FREQUENCY'] == 'Q')) & (df_CPI['SUBJECT'] == 'CPALTT01')]
df_LTRATES_filtered = df_LTRATES[(df_LTRATES['FREQUENCY'] == 'M') & (df_LTRATES['SUBJECT'] == 'IRLT')]

df_CPI_filtered.to_csv('OECD_CPI_Data.csv', index=False)
df_LTRATES_filtered.to_csv('OECD_LTRATES_Data.csv', index=False)