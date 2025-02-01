import os
import pandas as pd
from glob import glob
import re

def dealerships(input_folder, output_folder):
    """
    Processes all CSV files in the given input folder, extracts dealership bike counts,
    and saves a summary for each file with a matching date in the output folder.
    
    Parameters:
    - input_folder (str): Path to the folder containing raw CSV files.
    - output_folder (str): Path to the folder where summary files will be saved.
    """

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Find all CSV files recursively in the input folder
    file_paths = glob(os.path.join(input_folder, "**", "*.csv"), recursive=True)
    
    # Process each file separately
    for file in file_paths:
        print(f"Processing: {os.path.basename(file)}")
        
        try:
            # Extract date from filename (assuming format: autotrader_data_YYYY-MM-DD.csv)
            match = re.search(r'autotrader_data_(\d{4}-\d{2}-\d{2})\.csv', file)
            if match:
                file_date = match.group(1)
            else:
                print(f"Skipping {os.path.basename(file)} - Unable to extract date from filename")
                continue

            # Load file into a DataFrame
            df = pd.read_csv(file, delimiter="\t")  # Adjust delimiter if needed

            # Ensure at least required columns exist
            if df.shape[1] < 3 or 'Dealership Name' not in df.columns:
                print(f"Skipping {os.path.basename(file)} - Missing required columns")
                continue

            # Drop duplicates across all columns
            df = df.drop_duplicates()
            print(os.path.basename(file), "has ", len(df), "entries after deduplication")

            # Extract Dealership name and bike count
            df['Dealership'] = df['Dealership Name'].str.split(" - ").str[0]
            df['Bike Count'] = df['Dealership Name'].str.extract(r'See all (\d+) bikes')[0].astype(float)

            # Create a dealership summary DataFrame
            df_dealership_summary = df[['Dealership', 'Bike Count']].drop_duplicates()
            df_dealership_summary = df_dealership_summary.sort_values(by='Bike Count', ascending=False)

            # Define the output file path
            summary_file = os.path.join(output_folder, f"dealership_summary_{file_date}.csv")

            # Save dealership summary to the output folder
            df_dealership_summary.to_csv(summary_file, index=False)
            print(f"✅ Dealership summary saved at: {summary_file}")

        except Exception as e:
            print(f"❌ Error processing {file}: {e}")

    print("✅ All files processed successfully!")
