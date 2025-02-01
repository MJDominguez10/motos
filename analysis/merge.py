import os
import pandas as pd
from glob import glob
import re
from datetime import datetime

def merge(data_folder: str, output_filename: str = "cleaned_autotrader_data.csv"):
    """
    Process the raw data from CSV files within the specified folder, clean it, and save the result.

    :param data_folder: The folder containing the raw CSV files.
    :param output_filename: The name of the cleaned CSV file to be saved. Defaults to "cleaned_autotrader_data.csv".
    """

    # Find all CSV files recursively
    file_paths = glob(os.path.join(data_folder, "**", "*.csv"), recursive=True)

    # List to store dealership summary
    dealership_data = []

    # List to store data from all files
    all_data = []

    # Process each file
    for file in file_paths:
        print(f"Processing: {os.path.basename(file)}")
        
        try:
            # Load file into a DataFrame
            df = pd.read_csv(file, delimiter="\t")  # Adjust delimiter if needed

            # Ensure at least required columns exist
            if df.shape[1] < 3:
                print(f"Skipping {file} - Less than 3 columns")
                continue

            # Drop duplicates across all columns
            df = df.drop_duplicates()
            print(os.path.basename(file), "has ", len(df))

            # Cleaning and transforming data
            if 'Mileage' in df.columns:
                df['Mileage'] = df['Mileage'].astype(str).str.extract(r'(\d+[,.]?\d*)')[0]
                df['Mileage'] = df['Mileage'].str.replace(",", "", regex=True).astype(float)

            if 'Price' in df.columns:
                df['Price'] = df['Price'].astype(str).str.replace("£", "", regex=False)
                df['Price'] = df['Price'].str.replace(",", "", regex=False).astype(float)

            if 'Owner' in df.columns:
                df['Owner'] = df['Owner'].astype(str).str.extract(r'(\d+)')[0]
                df['Owner'] = pd.to_numeric(df['Owner'], errors='coerce')

            if 'Year' in df.columns:
                df['Year'] = df['Year'].astype(str).str.extract(r'(\d{4})')[0]
                df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

            # Extract 'Make' and 'Model'
            df[['Make', 'Model']] = df['Name'].str.split(" ", n=1, expand=True)

            # Append processed data
            all_data.append(df)

        except Exception as e:
            print(f"Error processing {file}: {e}")

    # Merge all cleaned data
    if all_data:
        df_unique = pd.concat(all_data, ignore_index=True).drop_duplicates()

        # Merge all dealership data
        if dealership_data:
            df_dealership_summary = pd.concat(dealership_data, ignore_index=True).drop_duplicates()
        else:
            df_dealership_summary = pd.DataFrame(columns=['Dealership', 'Bike Count'])

        # Sort by Bike Count
        df_dealership_summary = df_dealership_summary.sort_values(by='Bike Count', ascending=False)

        # Save full cleaned data
        output_file = os.path.join(data_folder, output_filename)
        df_unique.to_csv(output_file, index=False)
        print(f"✅ Data cleaning complete! Cleaned data saved at: {output_file}")

    else:
        print("⚠️ No valid data found in CSV files.")
