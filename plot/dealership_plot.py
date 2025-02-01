# dealership_plot.py
import plotly.express as px
from data_processing import load_dealership_data

# Load the processed dealership data
df_grouped = load_dealership_data()

# Function to update dealership graph
def update_dealership_graph(search_value):
    if search_value:
        filtered_df = df_grouped[df_grouped['Dealership'].str.contains(search_value, case=False, na=False)]
    else:
        filtered_df = df_grouped

    fig = px.line(filtered_df, x='Date', y='Bike Count', color='Dealership', title="Motorbikes in Dealerships Over Time")
    fig.update_traces(mode='lines+markers')
    fig.update_layout(xaxis_title='Date', yaxis_title='Bike Count', xaxis=dict(tickformat="%Y-%m-%d", tickangle=45))
    return fig
