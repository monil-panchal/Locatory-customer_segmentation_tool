from dash import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import os
from src.user.customer import Customer
import pandas as pd
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

mapbox_access_token = 'pk.eyJ1IjoiYWhzLXZhIiwiYSI6ImNraGsyMWVmdDByOWszNnNkdzJqcHpwOWMifQ.llITOAaVvDUflVgenIPPlw'

# print(mapbox_access_token[0:10])
customer = Customer()

app.layout = html.Div([
    html.H1('Welcome to Locatory app'),

    # Borough_checklist
    dbc.FormGroup([
        dbc.Label("Choose Dataset"),
        dcc.Dropdown(id="dropdown", value=1,
                     options=[{"label": "First Data", "value": 1}, {"label": "Second Data", "value": 2}]),
    ]),
    #map
    html.Div([
        dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True},
                  style={'padding-bottom':'2px', 'height': '100vh'})
    ])
])

@app.callback(Output('graph', 'figure'), [Input('dropdown', 'value')])
def update_fig(value):
    customer_df = pd.DataFrame(customer.get_customer_data())
    print(customer_df[0:10])
    locations = [go.Scattermapbox(
        lon=customer_df['long'],
        lat=customer_df['lat'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=6
        ),
    )]
    return {
        'data': locations,
        'layout': go.Layout(
            uirevision='foo',
            clickmode='event+select',
            hovermode='closest',
            hoverdistance=2,
            title=dict(text="MapBox", font=dict(size=50, color='green')),
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                style='light',
                center=dict(
                    lat=-22.80105,
                    lon=-45.945155
                ),
                pitch=0,
                zoom=3
            ),
        )
    }

if __name__ == '__main__':
    # ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    # print(ROOT_DIR)
    # app.config.from_yaml(os.join(ROOT_DIR, 'config/config.yml'))
    app.run_server(debug=True)
