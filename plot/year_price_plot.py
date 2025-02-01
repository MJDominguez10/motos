import plotly.express as px
from data_processing import load_autotrader_data

# Load the Autotrader data
df_autotrader = load_autotrader_data()

# Function to update Year vs Price graph
def update_year_vs_price(selected_year_range):
    min_year, max_year = selected_year_range
    filtered_df = df_autotrader[
        (df_autotrader['Year'] >= min_year) & (df_autotrader['Year'] <= max_year)
    ]

    # Create a custom hover text
    filtered_df['hover_text'] = (
        "Make: " + filtered_df['Make'] + "<br>" +
        "Model: " + filtered_df['Model'] + "<br>" +
        "Year: " + filtered_df['Year'].astype(str) + "<br>" +
        "Price: £" + filtered_df['Price'].astype(str) + "<br>" +
        "Mileage: " + filtered_df['Mileage'].astype(str) + " miles"  # Example for mileage
    )

    # Create the scatter plot
    fig = px.scatter(
        filtered_df, 
        x='Year', 
        y='Price', 
        color='Make', 
        title="Year vs Price",
        hover_name='hover_text',  # Use the custom hover text
    )
    
    fig.update_layout(
        xaxis_title='Year of Manufacture',
        yaxis_title='Price',
        xaxis=dict(tickmode='linear'),
    )
    
    return fig
