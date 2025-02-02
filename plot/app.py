import os
import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from dealership_plot import update_dealership_graph
from brand_plot import update_brand_graph
from mileage_price_plot import update_mileage_vs_price
from year_price_plot import update_year_vs_price  # New Import

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout with main title, images, and subtitles for each graph section
app.layout = dbc.Container([
    # Row for the images at the top-left and top-right
    dbc.Row([
        dbc.Col(html.Img(src='assets/bmw.jpg', style={'height': '200px', 'width': 'auto'}), width=2),
        dbc.Col(html.H1("Manolo Dashboard for Motorbikes", className="text-center mb-4"), width=8),
        dbc.Col(html.Img(src='assets/HD.png', style={'height': '200px', 'width': 'auto'}), width=2),
    ], className="mb-4"),

    # Dealership Search Section
    dbc.Row([
        dbc.Col(html.H2("Bikes in Dealerships Over Time", className="text-center mb-4"), width=12),
        dbc.Col([
            html.Label('Search Dealership:'),
            dcc.Input(id='dealership-search', type='text', placeholder='Enter dealership name...', debounce=True),
        ], width=6, className="mx-auto"),
    ], className="mb-5"),
    dcc.Graph(id='bike-count-graph'),

    # Brand Search Section
    dbc.Row([
        dbc.Col(html.H2("Total Bikes by Brand Over Time", className="text-center mb-4"), width=12),
        dbc.Col([
            html.Label('Search Brand:'),
            dcc.Input(id='brand-search', type='text', placeholder='Enter brand name...', debounce=True),
        ], width=6, className="mx-auto"),
    ], className="mb-5"),
    dcc.Graph(id='brand-bike-count-graph'),

    # Mileage vs Price Section
    dbc.Row([
        dbc.Col(html.H2("Mileage vs Price of Bikes", className="text-center mb-4"), width=12),
        dbc.Col([
            html.Label('Search Mileage Range:'),
            dcc.RangeSlider(
                id='mileage-slider',
                min=0,
                max=200000,
                step=100,
                marks={i: str(i) for i in range(0, 200000, 20000)},
                value=[0, 200000],
            ),
        ], width=8, className="mx-auto"),
    ], className="mb-5"),
    dcc.Graph(id='mileage-vs-price-graph'),

    # Year vs Price Section
    dbc.Row([
        dbc.Col(html.H2("Year vs Price of Bikes", className="text-center mb-4"), width=12),
        dbc.Col([
            html.Label('Search Year Range:'),
            dcc.RangeSlider(
                id='year-slider',
                min=1950,
                max=2025,
                step=1,
                marks={i: str(i) for i in range(1990, 2026, 5)},
                value=[1950, 2025],
            ),
        ], width=8, className="mx-auto"),
    ], className="mb-5"),
    dcc.Graph(id='year-vs-price-graph'),

], fluid=True)

# Callbacks to update the graphs based on input
@app.callback(
    Output('bike-count-graph', 'figure'),
    Input('dealership-search', 'value')
)
def update_dealership_graph_callback(search_value):
    return update_dealership_graph(search_value)

@app.callback(
    Output('brand-bike-count-graph', 'figure'),
    Input('brand-search', 'value')
)
def update_brand_graph_callback(search_value):
    return update_brand_graph(search_value)

@app.callback(
    Output('mileage-vs-price-graph', 'figure'),
    Input('mileage-slider', 'value')
)
def update_mileage_vs_price_callback(selected_mileage_range):
    return update_mileage_vs_price(selected_mileage_range)

@app.callback(
    Output('year-vs-price-graph', 'figure'),
    Input('year-slider', 'value')
)
def update_year_vs_price_callback(selected_year_range):
    return update_year_vs_price(selected_year_range)

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Get PORT from environment
    app.run_server(host='0.0.0.0', port=port, debug=False)
