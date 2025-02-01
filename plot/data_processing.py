import os
import pandas as pd
from glob import glob

# Define the path to the data folder
data_folder = './data2plot/Dealerships/'

# Load and process the dealership data
def load_dealership_data():
    file_paths = glob(os.path.join(data_folder, 'dealership_summary_*.csv'))
    all_data = []

    for file in file_paths:
        date_str = os.path.basename(file).split('_')[-1].split('.')[0]
        date = pd.to_datetime(date_str, format='%Y-%m-%d')

        df = pd.read_csv(file)
        df['Date'] = date
        all_data.append(df)

    df_combined = pd.concat(all_data, ignore_index=True)
    df_combined['Bike Count'] = pd.to_numeric(df_combined['Bike Count'], errors='coerce')
    df_combined = df_combined.drop_duplicates(subset=['Dealership', 'Date'])
    df_combined = df_combined[df_combined['Bike Count'] <= 1100]
    df_grouped = df_combined.groupby(['Dealership', 'Date'], as_index=False)['Bike Count'].sum()
    return df_grouped

# Load and process the Autotrader data
# data_processing.py
def load_autotrader_data():
    autotrader_data_path = './data2plot/cleaned_autotrader_data.csv'
    df_autotrader = pd.read_csv(autotrader_data_path)

    # Debug: Check the columns to make sure 'Mileage' exists
    print("Columns in Autotrader Data:", df_autotrader.columns)
    
    # Ensure proper data types
    df_autotrader['Date Collected'] = pd.to_datetime(df_autotrader['Date Collected'], format='%Y-%m-%d')
    
    return df_autotrader  # Return the raw dataset, not the grouped one

