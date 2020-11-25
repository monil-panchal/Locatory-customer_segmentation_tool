import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from apps.user.customer import Customer
from dash.dependencies import Input, Output, State
from app import app
from apps.config.constants import brazil_state_code_map, mapbox_access_token

select_country_div = html.Div([
                        dbc.Label("Select Country"),
                        dcc.Checklist(
                            id="country_checkbox",
                            options=[

                            ],
                            value=['Brazil'],
                            labelStyle={'display': 'inline-block'}
                        ),
                        ])

select_state_div = html.Div([
                        dbc.Label("Select State"),
                        dcc.Dropdown(
                            id="state_dropdown",
                            options=[

                            ],
                            value=[],
                            multi=True,
                        ),
                        ])

select_city_div = html.Div([
                        dbc.Label("Select City"),
                        dcc.Dropdown(
                            id="city_dropdown",
                            options=[
                            ],
                            value=[],
                            multi=True,
                            ),
                        ])

select_gender_div = html.Div([
                        dbc.Label("Select Gender"),
                        dcc.Checklist(
                            id="gender_checkbox",
                            options=[

                            ],
                            value=['Male'],
                            labelStyle={'display': 'inline-block'}
                        ),
                        ])

select_age_range_div = html.Div([
                    html.H6('Select Age Range (in years)'),
                    dcc.RangeSlider(
                        id='age-range-slider',
                        step=1,
                    ),
                    html.Div(id='output-container-range-slider-age', style={'textAlign': 'center'})
                    ])

select_income_range_div = html.Div([
                    html.H6('Select Income Range'),
                    dcc.RangeSlider(
                        id='income-range-slider',
                            step = 100,
                    ),
                    html.Div(id='output-container-range-slider-income', style={'textAlign': 'center'})
                    ])

layout = dbc.Container([
            html.H2('Map Dashboard'),
            html.Hr(),
            dbc.Row([
                    dbc.Col(
                        select_country_div,
                     width="2"),
                    dbc.Col(
                        select_state_div
                        ,width="10"
                    ),
                ]),
            dbc.Row([
                    dbc.Col(
                        select_city_div,
                    width="10"),
                    dbc.Col(
                        select_gender_div,
                     width="2"),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col(
                    select_age_range_div,
                    width="6"),
                dbc.Col(
                    select_income_range_div,
                width="6"),
            ]),
            # map
            html.Div([
                dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True},
                          style={'padding-bottom': '2px', 'height': '100vh'})
            ])
        ], className="mt-4")

@app.callback(
    Output('output-container-range-slider-age', 'children'),
    [Input('age-range-slider', 'value')])
def update_age_range_div(value):
    return 'Selected Age Range "{}"'.format(value)

@app.callback(
    Output('output-container-range-slider-income', 'children'),
    [Input('income-range-slider', 'value')])
def update_income_range_div(value):
    return 'Selected Income Range: "{}"'.format(value)

@app.callback(
        Output('state_dropdown', 'options'), Output('state_dropdown', 'value'),
        [Input('country_checkbox', 'value')],
        )
def update_state_dropdown(value):
    print(f"options",value)
    customer = Customer()
    customer_df = pd.DataFrame(customer.get_customer_data())
    df = customer_df.loc[customer_df['customer_country'].isin(value)]
    states = sorted(df['customer_state'].unique())
    return [
        {'label': f"{brazil_state_code_map[key]}", 'value': key} for key in states
    ], states[0:1]

@app.callback(
        Output('city_dropdown', 'options'), Output('city_dropdown', 'value'),
        [Input('state_dropdown', 'value')],
        )
def update_city_dropdown(value):
    print(f"options",value)
    customer = Customer()
    customer_df = pd.DataFrame(customer.get_customer_data())
    unique_cities = customer_df.loc[customer_df['customer_state'].isin(value)]['customer_city'].unique()
    return [
        {'label': f"{key}", 'value': key} for key in unique_cities
    ], unique_cities

@app.callback(Output('graph', 'figure'), [Input('gender_checkbox', 'value'), Input('age-range-slider', 'value'),
                                          Input('income-range-slider', 'value'), Input('country_checkbox', 'value'),
                                          Input('state_dropdown', 'value')])
def update_fig(gender_values, age_range, income_range, countries, states):
    print(age_range, gender_values, income_range, countries, states)
    customer = Customer()
    customer_df = pd.DataFrame(customer.get_customer_data())
    df = customer_df
    print(customer_df[0:3])
    if countries is not None:
        df = df.loc[df['customer_country'].isin(countries)]
    if states is not None:
        df = df.loc[df['customer_state'].isin(states)]
    if gender_values is not None:
        df = df.loc[df['gender'].isin(gender_values)]
        print(len(df), len(df['gender'].isin(gender_values)))
    if age_range is not None and len(age_range) == 2:
        df = df.loc[(df['age'] >= age_range[0]) & (df['age'] <= age_range[1])]
    if income_range is not None and len(income_range) == 2:
        df = df.loc[(df['income'] >= income_range[0]) & (df['income'] <= income_range[1])]

    locations = [go.Scattermapbox(
        lon=df['long'],
        lat=df['lat'],
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

@app.callback(Output('country_checkbox', 'options'),
            Output('gender_checkbox', 'options'), Output('age-range-slider', 'min'),
            Output('age-range-slider', 'max'), Output('age-range-slider', 'value'),
            Output('age-range-slider', 'marks'), Output('income-range-slider', 'min'),
            Output('income-range-slider', 'max'), Output('income-range-slider', 'value'),
            Output('income-range-slider', 'marks'),
              [Input('url', 'href')])
def display_page(href):
    print(href)
    country_checkbox_options = []
    gender_checkbox_options = []
    age_range_slider_min = 0
    age_range_slider_max = 0
    age_range_slider_value = []
    age_range_slider_marks = {}
    income_range_slider_min = 0
    income_range_slider_max = 0
    income_range_slider_value = []
    income_range_slider_marks = {}
    print('Called on page loading via url in map')
    if href is not None and 'map_dashboard' == href.split('/')[-1]:
        customer = Customer()
        customer_df = pd.DataFrame(customer.get_customer_data())
        country_checkbox_options = [{'label': key, 'value': key} for key in sorted(customer_df['customer_country'].unique())]
        gender_checkbox_options = [{'label': key, 'value': key} for key in sorted(customer_df['gender'].unique())]
        age_range_slider_min = customer_df['age'].min()
        age_range_slider_max = customer_df['age'].max()
        age_range_slider_value = [customer_df['age'].min(), customer_df['age'].min() + 3]
        age_range_slider_marks = {int(key): {'label': f"{key}"} for key in range(0, customer_df['age'].max() + 1, 5)}
        income_range_slider_min = customer_df['income'].min()
        income_range_slider_max = customer_df['income'].max()
        income_range_slider_value = [customer_df['income'].min(), customer_df['income'].min() + 5000]
        income_range_slider_marks = {int(key): {'label': f"{key}"} for key in range(0, customer_df['income'].max() + 1, 5000)}

    return country_checkbox_options, \
           gender_checkbox_options, \
           age_range_slider_min, \
           age_range_slider_max, \
           age_range_slider_value, \
           age_range_slider_marks, \
           income_range_slider_min, \
           income_range_slider_max, \
           income_range_slider_value, \
           income_range_slider_marks