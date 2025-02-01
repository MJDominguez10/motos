import plotly.express as px
from data_processing import load_autotrader_data

# Load the Autotrader data
df_autotrader = load_autotrader_data()

# Function to update Mileage vs Price graph
def update_mileage_vs_price(selected_mileage_range):
    min_mileage, max_mileage = selected_mileage_range
    filtered_df = df_autotrader[(df_autotrader['Mileage'] >= min_mileage) & (df_autotrader['Mileage'] <= max_mileage)]

    # Create a custom hover text
    filtered_df['hover_text'] = (
        "Make: " + filtered_df['Make'] + "<br>" +
        "Model: " + filtered_df['Model'] + "<br>" +
        "Year: " + filtered_df['Year'].astype(str) + "<br>" +
        "Price: £" + filtered_df['Price'].astype(str) + "<br>" +
        "Mileage: " + filtered_df['Mileage'].astype(str) + " miles"
    )

    # Create the scatter plot
    fig = px.scatter(
        filtered_df, 
        x='Mileage', 
        y='Price', 
        color='Make', 
        title="Mileage vs Price",
        hover_name='hover_text',  # Use the custom hover text
    )

    fig.update_layout(
        xaxis_title='Mileage',
        yaxis_title='Price',
    )

    return fig
