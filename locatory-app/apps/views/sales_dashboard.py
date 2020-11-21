import cards as cards
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from apps.user.sales import Sales

from app import app

time_line = {}
geo_data = {}


def fetch_timelines():
    global time_line
    time_line = Sales().fetch_timeline()
    return time_line


def fetch_geo_info():
    global geo_data
    geo_data = Sales().fetch_geo_info()
    return geo_data


card_content_1 = [
    dbc.CardHeader("Filter by timeline"),
    dbc.CardBody(
        [
            dbc.FormGroup([
                dbc.Label("Year"),
                dcc.Dropdown(
                    id='year-selector',
                )
            ]),
            dbc.FormGroup([
                dbc.Label("Month"),
                dcc.Dropdown(
                    id='month-selector',
                )
            ]),
        ]
    ),

]

card_content_2 = [
    dbc.CardHeader("Filter by region"),
    dbc.CardBody(
        [
            dbc.FormGroup([
                dbc.Label("Country"),
                dcc.Dropdown(
                    id='country-selector',
                )
            ]),
            dbc.FormGroup([
                dbc.Label("State"),
                dcc.Dropdown(
                    id='state-selector',
                )
            ]),
            dbc.FormGroup([
                dbc.Label("City"),
                dcc.Dropdown(
                    id='city-selector',
                )
            ]),
            html.Button('View Dashboard', id='view_dashboard', n_clicks=0, className='btn btn-primary'),
        ]
    )
]

card_sales_dashboard = [
    dbc.CardHeader("sales Dashboard"),
    dbc.CardBody(
        [
            html.Div(id='sales_dashboard')
        ]
    ),

]

layout = dbc.Container([
    html.H2('Sales Dashboards'),
    html.Hr(),
    html.Div([
        dbc.Card(card_content_1, ),
        dbc.Card(card_content_2, ),

    ], id='menu', style={'width': 200}),
    html.Div(id='output'),
    html.Div(card_sales_dashboard)
], className="mt-4")


@app.callback([Output('output', 'children'),
               Output('year-selector', 'options'),
               Output('country-selector', 'options')],
              [Input('url', 'href')])
def display_page(href):
    print(f'href is:{href}')
    print('Called on page loading via url in sales')
    if href is not None and 'sales_dashboard' in href:
        print('loading sales dashboard data')
        geo_data = fetch_geo_info()
        time_line = fetch_timelines()

        countries = []
        for i in geo_data:
            countries.append(i['_id'])

        return '', \
               [{'label': i, 'value': i} for i in sorted(time_line.keys(), reverse=True)], \
               [{'label': i, 'value': i} for i in countries]

    else:
        print('hiding sales dashboard data')
        raise PreventUpdate


@app.callback(Output('month-selector', 'options'),
              Input('year-selector', 'value'))
def display_timeline_data(year):
    print(f'selected year is:{year}')
    if year is not None:
        months = time_line[year]
        return [{'label': i, 'value': i} for i in sorted(months)]

    else:
        return []


@app.callback(Output('state-selector', 'options'),
              Input('country-selector', 'value'))
def display_geo_data_states(country):
    if country is not None:

        state_list = []
        for x in geo_data:
            if x['_id'] == country:
                states = x['States']
                for s in states:
                    state_list.append(s['state'])

        return [{'label': i, 'value': i} for i in sorted(state_list)]

    else:
        return []


@app.callback(Output('city-selector', 'options'),
              [Input('country-selector', 'value'),
               Input('state-selector', 'value')
               ])
def display_geo_data_cities(country, state):
    if not None in [country, state]:

        city_list = []
        for x in geo_data:
            if x['_id'] == country:
                states = x['States']
                for s in states:
                    if s['state'] == state:
                        city = s['City']
                        for c in city:
                            city_list.append(c['City'])

        return [{'label': i, 'value': i} for i in sorted(city_list)]

    else:
        return []

# @app.callback(
#     Output('sales_dashboard', 'children'),
#     Input('view_dashboard', 'n_clicks'))
# def submit_dashboard_request(n_clicks):
#     print(f'selected n_click is: {n_clicks}')
#     return ''


@app.callback(
    Output('sales_dashboard', 'children'),
    Input('view_dashboard', 'n_clicks'),
    [State('year-selector', 'value'),
     State('month-selector', 'value'),
     State('country-selector', 'value'),
     State('state-selector', 'value'),
     State('city-selector', 'value')])
def submit_dashboard_request(n_clicks, year, month, country, state, city):
    print(n_clicks)
    if n_clicks is not None and int(n_clicks) > 0:
        print(f'selected year is: {year}')
        print(f'selected month is: {month}')
        print(f'selected country is: {country}')
        print(f'selected state is: {state}')
        print(f'selected city is: {city}')
    return ''