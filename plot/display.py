

import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from glob import glob

# Initialize Dash app
app = dash.Dash(__name__)

# Define the directory containing the CSV files
data_folder = './data2plot/Dealerships/'

# Use glob to get all CSV files in the folder (including subfolders if any)
file_paths = glob(os.path.join(data_folder, 'dealership_summary_*.csv'))

# List to store data
all_data = []

# Process each file for dealership bike counts
for file in file_paths:
    # Extract the date from the filename (assumes format dealership_summary_YYYY-MM-DD.csv)
    date_str = os.path.basename(file).split('_')[-1].split('.')[0]  # Extract date (YYYY-MM-DD)
    date = pd.to_datetime(date_str, format='%Y-%m-%d')
    
    # Debug: print the extracted date to ensure it's correct
    print(f"Processing file: {file} - Date extracted: {date}")

    # Load the file into a DataFrame
    df = pd.read_csv(file)
    
    # Add the 'Date' column to the DataFrame
    df['Date'] = date
    
    # Append the data to the all_data list
    all_data.append(df)

# Concatenate all data into a single DataFrame
df_combined = pd.concat(all_data, ignore_index=True)

# Debug: print unique dates to verify
print("Unique Dates in Data:", df_combined['Date'].unique())

# Ensure proper data types for Bike Count and remove any invalid entries
df_combined['Bike Count'] = pd.to_numeric(df_combined['Bike Count'], errors='coerce')

# Remove duplicates for each dealership and date
df_combined = df_combined.drop_duplicates(subset=['Dealership', 'Date'])

# Optionally filter out unreasonable bike counts (e.g., above 1100)
df_combined = df_combined[df_combined['Bike Count'] <= 1100]

# Group by Dealership and Date, summing the Bike Count
df_grouped = df_combined.groupby(['Dealership', 'Date'], as_index=False)['Bike Count'].sum()

# Debug: check the first few rows of the grouped data
print("Grouped Data (Dealership, Date, Bike Count):")
print(df_grouped.head())

# Step 2: Load and process the cleaned_autotrader_data.csv for bike count by brand and date
autotrader_data_path = './data2plot/cleaned_autotrader_data.csv'

# Load the cleaned Autotrader data
df_autotrader = pd.read_csv(autotrader_data_path)

# Convert the 'Date Collected' to datetime and 'Bike Count' to numeric (assuming it's represented by count of rows per brand)
df_autotrader['Date Collected'] = pd.to_datetime(df_autotrader['Date Collected'], format='%Y-%m-%d')

# Group by Make (brand) and Date Collected to count the number of bikes per day per brand
df_autotrader_grouped = df_autotrader.groupby(['Make', 'Date Collected'], as_index=False).size().rename(columns={'size': 'Bike Count'})

# Debug: check the first few rows of the autotrader grouped data
print("Autotrader Grouped Data (Make, Date Collected, Bike Count):")
print(df_autotrader_grouped.head())

# Step 3: Build the layout of the dashboard
app.layout = html.Div(children=[
    html.H1("Motorbikes in Dealerships Over Time", style={'text-align': 'center'}),
    
    # Input field for searching dealership names in the legend
    html.Div([
        html.Label('Search Dealership:'),
        dcc.Input(id='dealership-search', type='text', placeholder='Enter dealership name...', debounce=True),
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),
    
    # First line chart to display the bike count trend over time for all dealerships
    dcc.Graph(id='bike-count-graph'),

    # Input field for searching brand names in the legend
    html.Div([
        html.Label('Search Brand:'),
        dcc.Input(id='brand-search', type='text', placeholder='Enter brand name...', debounce=True),
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),

    # Second line chart to display the total bike count by brand over time
    dcc.Graph(id='brand-bike-count-graph'),

    # Input field for searching mileage in the plot
    html.Div([
        html.Label('Search Mileage Range:'),
        dcc.RangeSlider(
            id='mileage-slider',
            min=df_autotrader['Mileage'].min(),
            max=df_autotrader['Mileage'].max(),
            step=100,
            marks={i: str(i) for i in range(int(df_autotrader['Mileage'].min()), int(df_autotrader['Mileage'].max()), 1000)},
            value=[df_autotrader['Mileage'].min(), df_autotrader['Mileage'].max()],
        ),
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),

    # Scatter plot to display Mileage vs Price
    dcc.Graph(id='mileage-vs-price-graph'),
])

# Step 4: Callback to update the graph with all dealerships
@app.callback(
    Output('bike-count-graph', 'figure'),
    Input('dealership-search', 'value')  # Get the search value from the input field
)
def update_graph(search_value):
    # Filter data based on the search input (if provided)
    if search_value:
        # Filter dealerships based on search input (case insensitive)
        filtered_df = df_grouped[df_grouped['Dealership'].str.contains(search_value, case=False, na=False)]
    else:
        # If no search value, show all dealerships
        filtered_df = df_grouped

    # Create the line plot with dots (markers) connected by lines
    fig = px.line(filtered_df, x='Date', y='Bike Count', color='Dealership', title="Motorbikes in Dealerships Over Time")
    
    # Add the dealership name to customdata for each point
    fig.update_traces(customdata=filtered_df['Dealership'])
    
    # Add markers (dots) to the lines
    fig.update_traces(mode='lines+markers')  # This adds dots to the lines
    
    # Customize the hover template
    fig.update_traces(
        hovertemplate=
        '<b>Dealership:</b> %{customdata}<br>'  # Dealership name from customdata
        + '<b>Date:</b> %{x}<br>'  # Date
        + '<b>Bike Count:</b> %{y}<br>'  # Bike count
        + '<extra></extra>'  # Removes the extra info that Plotly shows by default (like trace name)
    )
    
    # Customize the layout
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Bike Count',
        legend_title='Dealership',
        xaxis=dict(tickformat="%Y-%m-%d", tickangle=45),  # Format the date and rotate labels
        width=1200,  # Adjust width for bigger plot
        height=600,  # Adjust height for bigger plot
        autosize=False,  # Ensure the plot size stays fixed
    )
    
    return fig

# Step 5: Callback to update the graph for brand bike counts
@app.callback(
    Output('brand-bike-count-graph', 'figure'),
    Input('brand-search', 'value')  # Get the search value from the input field for brand search
)
def update_brand_graph(search_value):
    # Filter data based on the search input (if provided)
    if search_value:
        # Filter brands based on search input (case insensitive)
        filtered_df = df_autotrader_grouped[df_autotrader_grouped['Make'].str.contains(search_value, case=False, na=False)]
    else:
        # If no search value, show all brands
        filtered_df = df_autotrader_grouped

    # Create the line plot for brand bike count over time with dots
    fig = px.line(filtered_df, x='Date Collected', y='Bike Count', color='Make', title="Total Bikes by Brand Over Time")
    
    # Add the brand name to customdata for each point
    fig.update_traces(customdata=filtered_df['Make'])
    
    # Add markers (dots) to the lines
    fig.update_traces(mode='lines+markers')  # This adds dots to the lines
    
    # Customize the hover template
    fig.update_traces(
        hovertemplate=
        '<b>Brand:</b> %{customdata}<br>'  # Brand name from customdata
        + '<b>Date:</b> %{x}<br>'  # Date
        + '<b>Bike Count:</b> %{y}<br>'  # Bike count
        + '<extra></extra>'  # Removes the extra info that Plotly shows by default (like trace name)
    )
    
    # Customize the layout
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Bike Count',
        legend_title='Brand',
        xaxis=dict(tickformat="%Y-%m-%d", tickangle=45),  # Format the date and rotate labels
        width=1200,  # Adjust width for bigger plot
        height=600,  # Adjust height for bigger plot
        autosize=False,  # Ensure the plot size stays fixed
    )
    
    return fig

# Step 6: Callback to update the Mileage vs Price scatter plot based on Mileage range slider
@app.callback(
    Output('mileage-vs-price-graph', 'figure'),
    Input('mileage-slider', 'value')  # Get the selected mileage range from the slider
)
def update_mileage_vs_price(selected_mileage_range):
    min_mileage, max_mileage = selected_mileage_range

    # Filter the Autotrader data based on the selected mileage range
    filtered_df = df_autotrader[(df_autotrader['Mileage'] >= min_mileage) & (df_autotrader['Mileage'] <= max_mileage)]

    # Create the scatter plot for Mileage vs Price
    fig = px.scatter(filtered_df, x='Mileage', y='Price', color='Make', title="Mileage vs Price")
    
    # Customize the hover template to display more detailed information
    fig.update_traces(
        hovertemplate=
        '<b>Bike Name:</b> %{customdata[0]}<br>'  # Bike Name from customdata
        + '<b>Year:</b> %{customdata[1]}<br>'  # Year of the bike
        + '<b>Model:</b> %{customdata[2]}<br>'  # Model of the bike
        + '<b>Mileage:</b> %{x} miles<br>'  # Mileage (x-axis)
        + '<b>Price:</b> £%{y}<br>'  # Price (y-axis)
        + '<extra></extra>'  # Removes the extra info that Plotly shows by default (like trace name)
    )
    
    # Add the relevant bike details to customdata for each point
    fig.update_traces(
        customdata=filtered_df[['Name', 'Year', 'Model']].values  # Add Name, Year, Model to customdata
    )
    
    # Customize the layout
    fig.update_layout(
        xaxis_title='Mileage',
        yaxis_title='Price',
        legend_title='Make',
        width=1200,  # Adjust width for bigger plot
        height=600,  # Adjust height for bigger plot
    )
    
    return fig

# Step 7: Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
