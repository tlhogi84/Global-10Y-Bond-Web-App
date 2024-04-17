import pandas as pd
import numpy as np

df_RATES = pd.read_csv('OECD_LTRATES_Data.csv')
df_CPI = pd.read_csv('OECD_CPI_Calcs.csv')

#I only want to retain these columns
selected_columns = ['LOCATION', 'Country', 'FREQUENCY','TIME', 'Value'] 
df_RATES = df_RATES.loc[:, selected_columns]

# Rename the "Value" column to "CPI Index"
df_RATES = df_RATES.rename(columns={'Value': 'LT_RATE'})
df_RATES = df_RATES.sort_values(by=['LOCATION', 'TIME'])
df_RATES['TIME'] = pd.to_datetime(df_RATES['TIME']) + pd.offsets.MonthEnd(0)

df_summary = df_RATES.groupby(['LOCATION', 'Country']).agg(
    Min_Time=('TIME', 'min'),
    Max_Time=('TIME', 'max'),
    Years=('TIME', lambda x: ((x.max() - x.min()).days) / 365.25)
).reset_index()

df_summary['Total_Months'] = ((df_summary['Max_Time'] - df_summary['Min_Time']).dt.days / 30).astype(int)

# Function to calculate missing months
def count_missing_months(row):
    time_range = pd.date_range(start=row['Min_Time'], end=row['Max_Time'], freq='M')
    present_months = pd.to_datetime(df_RATES[df_RATES['LOCATION'] == row['LOCATION']]['TIME'])
    missing_months = set(time_range) - set(present_months)
    return len(missing_months)

# Calculate the number of missing months for each country
df_summary['Missing_Months'] = df_summary.apply(count_missing_months, axis=1)

# Filter rows where Missing_Months is not zero
df_summary_non_zero = df_summary[df_summary['Missing_Months'] != 0]

# Create a list of locations with missing months
locations_to_interpolate = df_summary_non_zero['LOCATION'].tolist()

# Create an empty DataFrame to store the results
df_interpolated = pd.DataFrame()

# Iterate over each location with missing months
for location in locations_to_interpolate:
    # Filter rows for the current location
    df_location = df_RATES[df_RATES['LOCATION'] == location].copy()

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

# Fill NaN values in 'LT_RATE' column with appropriate values
df_interpolated['LT_RATE'] = df_interpolated.groupby(['LOCATION', 'Country'])['LT_RATE'].transform(lambda x: x.fillna(method='ffill'))

# Set the 'FREQUENCY' column to 'M*' to show it is interpolated
df_interpolated['FREQUENCY'] = 'M*'

# Create a mask for locations to filter out from df_RATES
locations_to_filter = df_summary_non_zero['LOCATION'].tolist()
filter_mask = df_RATES['LOCATION'].isin(locations_to_filter)

# Drop rows from df_RATES for locations to filter out
df_RATES_filtered = df_RATES[~filter_mask]

# Concatenate df_interpolated with df_RATES_filtered
df_RATES = pd.concat([df_RATES_filtered, df_interpolated], ignore_index=True)

# Sort df_RATES_concatenated by 'TIME' and 'LOCATION'
df_RATES = df_RATES.sort_values(by=['LOCATION', 'TIME'])

def calculate_duration(y):
    if y == 0:
        y = 0.0000000001  # Set a small value if yield is 0
    return (1 - (1 + y/100) ** -10) / (1 - (1 + y/100) ** -1)

def calculate_coupon_return(data):
    data['Coupon Return'] = data['LT_RATE'].shift(1) / 1200
    return data
    
def calculate_price_return(data):
    data['Price Return'] = -data['Duration'] * data['LT_RATE'].diff() / 100
    return data

df_RATES = df_RATES.sort_values(by=['LOCATION', 'TIME'])

df_RATES['Duration'] = df_RATES['LT_RATE'].apply(calculate_duration)

df_RATES = df_RATES.groupby('LOCATION', group_keys=False).apply(calculate_price_return).reset_index(drop=True)

df_RATES = df_RATES.groupby('LOCATION', group_keys=False).apply(calculate_coupon_return).reset_index(drop=True)

df_RATES['Total Return'] = df_RATES['Price Return'] + df_RATES['Coupon Return']

df_RATES['Total Return Index'] = df_RATES.groupby('LOCATION')['Total Return'].transform(
    lambda x: (1 + x).cumprod().fillna(1))

df_returns = df_RATES[['LOCATION', 'Country', 'TIME', 'LT_RATE']].copy()
df_returns['1Y Nominal Return']   = (df_RATES['Total Return Index'] / df_RATES.groupby('LOCATION')['Total Return Index'].shift(12)) - 1
df_returns['5Y Nominal Return']   = ((df_RATES['Total Return Index'] / df_RATES.groupby('LOCATION')['Total Return Index'].shift(60)) ** (1 / 5)) - 1
df_returns['20Y Nominal Return']  = ((df_RATES['Total Return Index'] / df_RATES.groupby('LOCATION')['Total Return Index'].shift(240)) ** (1 / 20)) - 1

df_returns['TIME'] = pd.to_datetime(df_returns['TIME'])
df_CPI['TIME'] = pd.to_datetime(df_CPI['TIME'])
df_returns = pd.merge(df_returns, df_CPI.drop(columns='FREQUENCY'), on=['LOCATION', 'TIME'], how='inner')
df_returns = df_returns.rename(columns={'Country_x': 'Country'})
df_returns = df_returns.drop(columns='Country_y')

df_returns = df_returns.sort_values(['LOCATION', 'TIME'])
df_returns['1Y Real Return']   = (1+df_returns['1Y Nominal Return'])/(1+df_returns['1Y Inflation'])-1
df_returns['5Y Real Return']   = (1+df_returns['5Y Nominal Return'])/(1+df_returns['5Y Inflation'])-1
df_returns['20Y Real Return']  = (1+df_returns['20Y Nominal Return'])/(1+df_returns['20Y Inflation'])-1

# Calculate forward returns (12 months, 60 months, and 240 months)
df_returns['Forward 1Y Nominal Return']  = df_returns.groupby('LOCATION')['1Y Nominal Return'].shift(-12)
df_returns['Forward 5Y Nominal Return']  = df_returns.groupby('LOCATION')['5Y Nominal Return'].shift(-60)
df_returns['Forward 20Y Nominal Return'] = df_returns.groupby('LOCATION')['20Y Nominal Return'].shift(-240)
df_returns['Forward 1Y Real Return']  = df_returns.groupby('LOCATION')['1Y Real Return'].shift(-12)
df_returns['Forward 5Y Real Return']  = df_returns.groupby('LOCATION')['5Y Real Return'].shift(-60)
df_returns['Forward 20Y Real Return'] = df_returns.groupby('LOCATION')['20Y Real Return'].shift(-240)

df_returns.to_csv("df_returns.csv")