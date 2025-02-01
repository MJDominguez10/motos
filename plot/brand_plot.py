# brand_plot.py
import plotly.express as px
from data_processing import load_autotrader_data

# Load the processed Autotrader data
df_autotrader_grouped = load_autotrader_data()


# Function to update the brand graph
def update_brand_graph(search_value):
    # Filter the data based on the search input (if provided)
    if search_value:
        filtered_df = df_autotrader_grouped[df_autotrader_grouped['Make'].str.contains(search_value, case=False, na=False)]
    else:
        filtered_df = df_autotrader_grouped
    
    # Group the data by 'Make' and 'Date Collected', and calculate the count of bikes for each group
    # This assumes that the 'Date Collected' column is already in datetime format.
    filtered_df_grouped = filtered_df.groupby(['Make', 'Date Collected']).size().reset_index(name='Bike Count')
    
    # Print the grouped data to check
    print(filtered_df_grouped)

    # Create the line plot using the grouped data
    fig = px.line(filtered_df_grouped, x='Date Collected', y='Bike Count', color='Make', title="Total Bikes by Brand Over Time")
    
    # Update plot traces to include both lines and markers
    fig.update_traces(mode='lines+markers')
    
    # Update layout with appropriate axis labels and date formatting
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Bike Count',
        xaxis=dict(tickformat="%Y-%m-%d", tickangle=45)
    )

    return fig

