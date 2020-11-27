import asyncio
# import cards as cards
import dash
import datetime as dt
import pandas as pd
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from apps.user.sales import Sales

from app import app
from apps.views.graphs.sales_bar_graph import generate_bar_graph_by_orders, generate_bar_graph_by_sales
from apps.views.graphs.sales_pie_chart import generate_pie_chart_by_location, generate_pie_chart_by_product_category
from apps.dataframe.process_sales_dashboard_df import add_year_month_week
from apps.views.graphs.sales_density_map import generate_density_map

time_line = {}
geo_data = {}
dashboard_data_stat = {}
current_df = pd.DataFrame
previous_df = pd.DataFrame


def process_current_dashboard_data(filter_data_options: dict, sales_dashboard_df: pd.DataFrame):
    global dashboard_data_stat
    if not sales_dashboard_df.empty:
        global current_df
        global previous_df

        if filter_data_options.get('year', None) is not None:
            if filter_data_options.get('month', None) is not None:
                current_df = sales_dashboard_df[
                    (sales_dashboard_df['order_date'].dt.year == filter_data_options.get('year')) &
                    (sales_dashboard_df['order_date'].dt.month == filter_data_options.get('month'))]
            else:
                current_df = sales_dashboard_df[
                    (sales_dashboard_df['order_date'].dt.year == filter_data_options.get('year'))]
            previous_df = sales_dashboard_df[~sales_dashboard_df.isin(
                current_df)].dropna(how='all')

        current_df = current_df.reset_index(drop=True)
        previous_df = previous_df.reset_index(drop=True)

        current_df, previous_df = add_year_month_week(current_df, previous_df)

        total_orders = current_df.shape[0]
        dashboard_data_stat['total_orders'] = total_orders

        total_sales = round(current_df['payment_value'].sum(), 2)
        dashboard_data_stat['total_sales'] = total_sales

        highest_order_value = round(current_df['payment_value'].max(), 2)
        dashboard_data_stat['highest_order_value'] = highest_order_value

        lowest_order_value = round(current_df['payment_value'].min(), 2)
        dashboard_data_stat['lowest_order_value'] = lowest_order_value

        average_order_value = round(current_df['payment_value'].mean(), 2)
        dashboard_data_stat['average_order_value'] = average_order_value

    else:
        for (x, y) in dashboard_data_stat.items():
            dashboard_data_stat[x] = 0
        pass


def fetch_timelines():
    global time_line
    time_line = Sales().fetch_timeline()
    time_line = dict(sorted(time_line.items(), reverse=True))

    for k, v in time_line.items():
        time_line[k] = sorted(time_line[k])

    print(f'time retrieved from db: {time_line} ')
    return time_line


def fetch_geo_info():
    global geo_data
    geo_data = Sales().fetch_geo_info()
    return geo_data


def calculate_previous_timeline_data(data: dict):
    print(f'data in fetch_previous_dashboard_data: {data}')
    """
    Previous year data fetching logic
    """
    current_year = data['year']
    prev_year = current_year - 1

    if prev_year not in time_line.keys():
        prev_year = current_year

    if data['month'] and data['month'] is not None:
        prev_month = data['month'] - 1

        if prev_month in time_line[current_year]:
            print(
                f'prev month: {prev_month} is in current year: {current_year} range')
            data['prev_month'] = prev_month

        else:
            print(
                f'prev month: {prev_month} is NOT in current year: {current_year} range. Fetching previous latest month')
            prev_month = time_line[prev_year] and time_line[prev_year][-1] or 1

            data['prev_year'] = prev_year
            data['prev_month'] = prev_month

            print(
                f'latest previous month is: {prev_month} of the year: {prev_year}')

    else:
        print(
            f'No month is selected in the filter. Fetching data of the previous year: {prev_year}')
        data['prev_year'] = prev_year

    return data


def fetch_current_dashboard_data(data: dict):
    data = calculate_previous_timeline_data(data)
    print(f'updated data dict: {data}')

    sales_dashboard_data = Sales().get_orders_for_dashboard(data)

    global current_df
    # current_df = pd.DataFrame(sales_dashboard_data)
    current_df = pd.json_normalize(sales_dashboard_data)
    process_current_dashboard_data(data, current_df)

    return data


"""
Card deck for dashboard statistics
"""
card_dashboard_stat = dbc.CardDeck(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Total Orders", className="card-title"),
                    html.H1(id='total_orders')
                ]
            ), color="dark", outline=True
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Total sales", className="card-title"),
                    html.Br(),
                    html.H4(id='total_sales', className="text-info")
                ]
            ), color="info", outline=True
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Highest order value", className="card-title"),
                    html.H4(id='highest_order_value',
                            className="text-success", )
                ]
            ), color="success", outline=True
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Lowest order value", className="card-title"),
                    html.Br(),
                    html.H4(id='lowest_order_value', className="text-danger")
                ]
            ), color="danger", outline=True
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Average order value", className="card-title"),
                    html.H4(id='average_order_value', className="text-warning")
                ]
            ), color="warning", outline=True
        )
    ]
)

"""
Card deck for bar chart visualization
"""
card_dashboard_bar_graphs = dbc.CardDeck(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dcc.Graph(id='bar_graph_orders')
                ]
            ), color="dark", outline=True
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    dcc.Graph(id='bar_graph_sales')
                ]
            ), color="dark", outline=True
        )
    ]
)

"""
Card deck for bar chart visualization
"""
card_dashboard_pie_graphs = dbc.CardDeck(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dcc.Graph(id='pie_chart_location')
                ]
            ), color="dark", outline=True
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    dcc.Graph(id='pie_chart_item_category')
                ]
            ), color="dark", outline=True
        )
    ]
)

"""
Card deck for bar chart visualization
"""
card_dashboard_map = dbc.CardDeck(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5('Sales by region'),
                    dcc.Graph(id='map_sales')
                ]
            ), color="dark", outline=True
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
            html.Button('View Dashboard', id='view_dashboard',
                        n_clicks=0, className='btn btn-primary'),
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
    html.Div(id='output', hidden=True),
    html.Div(id='sales_dashboard', hidden=True),
    html.H2('Sales Dashboards'),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Card(card_content_1, ),
                dbc.Card(card_content_2, ),

            ], id='menu', style={'position': 'sticky', 'top': '0'}),
        ], width='2'),


        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Card(card_dashboard_stat)
                    ], id='stat')
                ])
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Div(children=[
                        card_dashboard_bar_graphs
                    ], id='graphs')
                ]),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Div(children=[
                        card_dashboard_pie_graphs
                    ], id='graph_pie')
                ]),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        card_dashboard_map
                    ], id='graph_map')
                ]),
            ])
        ], width='10')
    ])
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
               [{'label': i, 'value': i} for i in time_line.keys()], \
               [{'label': i, 'value': i} for i in countries]

    else:
        print('hiding sales dashboard data')
        raise PreventUpdate


@app.callback(Output('month-selector', 'options'),
              Input('year-selector', 'value'))
def display_timeline_data(year):
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
     Output('average_order_value', 'children'),
     Output('bar_graph_orders', 'figure'),
     Output('bar_graph_sales', 'figure'),
     Output('pie_chart_location', 'figure'),
     Output('pie_chart_item_category', 'figure'),
     Output('map_sales', 'figure')],
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

            data = fetch_current_dashboard_data(data)

            if not (current_df.empty or previous_df.empty):
                if data.get('prev_month'):
                    bar_graph_type = 'month'
                else:
                    bar_graph_type = 'year'
                bar_graph_by_orders = generate_bar_graph_by_orders(
                    current_df, previous_df, bar_graph_type)
                bar_graph_by_sales = generate_bar_graph_by_sales(
                    current_df, previous_df, bar_graph_type)

                if data.get('state', None) is None:
                    pie_chart_type = 'country'
                elif not data.get('state') is None:
                    pie_chart_type = 'state'
                if not data.get('city') is None:
                    pie_chart_type = 'city'

                pie_chart_by_location = generate_pie_chart_by_location(
                    current_df, pie_chart_type)
                pie_chart_by_item_category = generate_pie_chart_by_product_category(
                    current_df)

                map_sales = generate_density_map(current_df)
            else:
                bar_graph_by_sales, \
                    bar_graph_by_orders, \
                    pie_chart_by_location, \
                    pie_chart_by_item_category, \
                    map_sales = {}, {}, {}, {}, {}

            return None, dashboard_data_stat.get('total_orders', 0), \
                "$ " + str(dashboard_data_stat.get('total_sales', 0.0)), \
                "$ " + str(dashboard_data_stat.get('highest_order_value', 0.0)), \
                "$ " + str(dashboard_data_stat.get('lowest_order_value', 0.0)), \
                "$ " + str(dashboard_data_stat.get('average_order_value', 0.0)), \
                bar_graph_by_orders, \
                bar_graph_by_sales, pie_chart_by_location, pie_chart_by_item_category, map_sales
    else:
        return None, None, None, None, None, None, {}, {}, {}, {}, {}
