import cards as cards
import dash
import pandas as pd
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from apps.user.sales import Sales

from app import app

time_line = {}
geo_data = {}
dashboard_data_stat = {}


def process_dashboard_data(sales_dashboard_df: pd.DataFrame):
    if not sales_dashboard_df.empty:
        print(f'sales_dashboard_df: {sales_dashboard_df.iloc[0]}')
        global dashboard_data_stat

        total_orders = sales_dashboard_df.shape[0]
        dashboard_data_stat['total_orders'] = total_orders

        total_sales = round(sales_dashboard_df['payment_value'].sum(), 2)
        dashboard_data_stat['total_sales'] = total_sales

        highest_order_value = round(sales_dashboard_df['payment_value'].max(), 2)
        dashboard_data_stat['highest_order_value'] = highest_order_value

        lowest_order_value = round(sales_dashboard_df['payment_value'].min(), 2)
        dashboard_data_stat['lowest_order_value'] = lowest_order_value

        average_order_value = round(sales_dashboard_df['payment_value'].mean(), 2)
        dashboard_data_stat['average_order_value'] = average_order_value

        print(f'updated dashboard_data_stat is: {dashboard_data_stat}')

    else:
        print('Zero records retrieved')
        for (x, y) in dashboard_data_stat.items():
            dashboard_data_stat[x] = 0
        pass


def fetch_timelines():
    global time_line
    time_line = Sales().fetch_timeline()
    return time_line


def fetch_geo_info():
    global geo_data
    geo_data = Sales().fetch_geo_info()
    return geo_data


def fetch_dashboard_data(data: dict):
    sales_dashboard_data = Sales().get_orders_for_dashboard(data)
    sales_dashboard_df = pd.DataFrame(sales_dashboard_data)

    process_dashboard_data(sales_dashboard_df)

    return sales_dashboard_df


"""
Card deck for dashboard statistics
"""
card_dashboard_stat = dbc.CardDeck(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Total Orders", className="card-title"),
                    html.Br(),
                    html.H1(id='total_orders')
                ]
            ), color="dark", outline=True
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Total sales", className="card-title"),
                    html.Br(), html.Br(),
                    html.H4(id='total_sales', className="text-info")
                ]
            ), color="info", outline=True
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Highest order value", className="card-title"),
                    html.Br(),
                    html.H4(id='highest_order_value', className="text-success", )
                ]
            ), color="success", outline=True
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Lowest order value", className="card-title"),
                    html.Br(), html.Br(),
                    html.H4(id='lowest_order_value', className="text-danger")
                ]
            ), color="danger", outline=True
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Average order value", className="card-title"),
                    html.Br(),
                    html.H4(id='average_order_value', className="text-warning")
                ]
            ), color="warning", outline=True
        )
    ]
)

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

layout = html.Div([
    html.H2('Sales Dashboards'),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Card(card_content_1, ),
                dbc.Card(card_content_2, ),

            ], id='menu'),
        ], width=2),
        dbc.Col([
            html.Div(children=[
                card_dashboard_stat
            ], id='stat')
        ], width=10)
    ]),

    html.Div(id='output', hidden=True),
    html.Div(id='sales_dashboard', hidden=True)

])


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


@app.callback(
    [Output('sales_dashboard', 'children'),
     Output('total_orders', 'children'),
     Output('total_sales', 'children'),
     Output('highest_order_value', 'children'),
     Output('lowest_order_value', 'children'),
     Output('average_order_value', 'children')],
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

        if not None in [year, country]:
            print('calling fetch sales data call')

            data = {
                'year': year,
                'month': month,
                'country': country,
                'state': state,
                'city': city
            }

            print(f'data: {data}')
            fetch_dashboard_data(data)
            return None, dashboard_data_stat.get('total_orders', 0), \
                   "$ " + str(dashboard_data_stat.get('total_sales', 0.0)), \
                   "$ " + str(dashboard_data_stat.get('highest_order_value', 0.0)), \
                   "$ " + str(dashboard_data_stat.get('lowest_order_value', 0.0)), \
                   "$ " + str(dashboard_data_stat.get('average_order_value', 0.0))
    else:
        return None, None, None, None, None, None
