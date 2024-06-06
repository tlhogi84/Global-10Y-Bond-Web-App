import pandas as pd
import numpy as np

df_CPI = pd.read_csv('OECD_CPI_Data.csv')

#I only want to retain these columns
selected_columns = ['LOCATION', 'Country', 'FREQUENCY','TIME', 'Value'] 
df_CPI = df_CPI.loc[:, selected_columns]

# Rename the "Value" column to "CPI Index"
df_CPI = df_CPI.rename(columns={'Value': 'CPI Index'})
df_CPI = df_CPI.sort_values(by=['LOCATION', 'TIME'])

# Filter rows where FREQUENCY is 'M'
df_m_frequency = df_CPI[df_CPI['FREQUENCY'] == 'M']

# Filter rows where FREQUENCY is 'Q' and LOCATION is either 'NZL' or 'AUS'
df_q_frequency_nzl_aus = df_CPI[(df_CPI['FREQUENCY'] == 'Q') & (df_CPI['LOCATION'].isin(['NZL', 'AUS']))]

# Concatenate the two filtered DataFrames
filtered_df = pd.concat([df_m_frequency, df_q_frequency_nzl_aus])

# Sort the final DataFrame by 'LOCATION' and 'TIME'
df_CPI = filtered_df.sort_values(by=['LOCATION', 'TIME'])

# Function to convert quarterly time to YYYY-MM-DD 
def convert_quarterly(row):
    if row['FREQUENCY'] == 'Q':
        year, quarter = row['TIME'][:4], int(row['TIME'][-1])
        month = (quarter - 1) * 3 + 1
        return pd.to_datetime(f"{year}-{month:02d}-01") - pd.DateOffset(months=1)
    elif row['FREQUENCY'] == 'M':
        return pd.to_datetime(row['TIME'])

# Apply the conversion function to create a new 'formatted_date' column
df_CPI['formatted_date'] = df_CPI.apply(convert_quarterly, axis=1)

# Drop both 'TIME' and 'Time' columns
df_CPI = df_CPI.drop(columns=['TIME'])

# Rename 'formatted_date' to 'TIME'
df_CPI = df_CPI.rename(columns={'formatted_date': 'TIME'})

# Sort the DataFrame by 'LOCATION' and 'TIME'
df_CPI = df_CPI.sort_values(by=['LOCATION', 'TIME'])

# Adjust all dates to month-end
df_CPI['TIME'] = pd.to_datetime(df_CPI['TIME']) + pd.offsets.MonthEnd(0)

# Create a DataFrame with required information
df_summary = df_CPI.groupby(['LOCATION', 'Country']).agg(
    Min_Time=('TIME', 'min'),
    Max_Time=('TIME', 'max'),
    Years=('TIME', lambda x: ((x.max() - x.min()).days) / 365.25)
).reset_index()

# Function to calculate missing months
def count_missing_months(row):
    time_range = pd.date_range(start=row['Min_Time'], end=row['Max_Time'], freq='M')
    present_months = pd.to_datetime(df_CPI[df_CPI['LOCATION'] == row['LOCATION']]['TIME'])
    missing_months = set(time_range) - set(present_months)
    return len(missing_months)

# Calculate the number of missing months for each country
df_summary['Missing_Months'] = df_summary.apply(count_missing_months, axis=1)

# Filter rows where Missing_Months is not zero
df_summary_non_zero = df_summary[df_summary['Missing_Months'] != 0]

missing_months_irl = set(pd.date_range(start='1955-02-28', end='2023-12-31', freq='M')) - set(pd.to_datetime(df_CPI[df_CPI['LOCATION'] == 'IRL']['TIME']))

df_CPI = df_CPI[~((df_CPI['LOCATION'] == 'IRL') & (df_CPI['TIME'] < '1975-11-01'))]

locations_to_interpolate = ['AUS', 'NZL']

# Create an empty DataFrame to store the results
df_interpolated = pd.DataFrame()

# Iterate over each location
for location in locations_to_interpolate:
    # Filter rows for the current location
    df_location = df_CPI[df_CPI['LOCATION'] == location].copy()

    # Convert 'TIME' column to datetime
    df_location['TIME'] = pd.to_datetime(df_location['TIME'])

    # Set 'TIME' as the index
    df_location = df_location.set_index('TIME')

    # Resample the data to monthly frequency and use linear interpolation
    df_location_resampled = df_location.resample('M').asfreq().interpolate(method='linear')

    # Reset the index and add the interpolated data to the result DataFrame
    df_location_resampled = df_location_resampled.reset_index()
    df_interpolated = pd.concat([df_interpolated, df_location_resampled])

# Create a mask for NaN values in the 'TIME' column
nan_mask = df_interpolated['TIME'].notna()

# Fill NaN values in 'LOCATION', 'Country', and 'FREQUENCY' based on the 'TIME' column
df_interpolated['LOCATION'] = np.where(nan_mask, df_interpolated['LOCATION'].ffill(), df_interpolated['LOCATION'])
df_interpolated['Country'] = np.where(nan_mask, df_interpolated['Country'].ffill(), df_interpolated['Country'])
df_interpolated['FREQUENCY'] = np.where(nan_mask, df_interpolated['FREQUENCY'].ffill(), df_interpolated['FREQUENCY'])

# Fill NaN values in 'CPI Index' column with appropriate values
df_interpolated['CPI Index'] = df_interpolated.groupby(['LOCATION', 'Country'])['CPI Index'].transform(lambda x: x.fillna(method='ffill'))

# Set the 'FREQUENCY' column to 'M*' to show it is interpolated
df_interpolated['FREQUENCY'] = 'M*'

# Create a mask for AUS and NZL rows in the original DataFrame
aus_nzl_mask = df_CPI['LOCATION'].isin(['AUS', 'NZL'])

# Drop AUS and NZL rows from df_CPI
df_CPI = df_CPI[~aus_nzl_mask]

# Concatenate df_interpolated with df_CPI
df_CPI = pd.concat([df_CPI, df_interpolated], ignore_index=True)
df_CPI = df_CPI.sort_values(by=['LOCATION', 'TIME'])

df_CPI['1Y Inflation']  = (df_CPI['CPI Index']/df_CPI.groupby('LOCATION')['CPI Index'].shift(12))  - 1
df_CPI['5Y Inflation']  = ((df_CPI['CPI Index']/df_CPI.groupby('LOCATION')['CPI Index'].shift(60)))**(1/5)  - 1
df_CPI['20Y Inflation'] = ((df_CPI['CPI Index']/df_CPI.groupby('LOCATION')['CPI Index'].shift(240)))**(1/20)  - 1

df_CPI.to_csv('OECD_CPI_Calcs.csv', index=False)