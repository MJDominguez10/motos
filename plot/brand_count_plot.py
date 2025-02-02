import plotly.express as px
from data_processing import load_autotrader_data

# Load the Autotrader data
df_autotrader = load_autotrader_data()

# Function to update Brand Count vs Date graph
def update_brand_count_over_time():
    df_grouped = df_autotrader.groupby(['Date', 'Make']).size().reset_index(name='Count')

    fig = px.scatter(
        df_grouped,
        x='Date',
        y='Count',
        color='Make',
        title="Number of Motorbikes per Brand Over Time",
        labels={'Date': 'Date', 'Count': 'Number of Bikes'},
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Bikes",
        xaxis=dict(tickmode="linear"),
    )

    return fig
