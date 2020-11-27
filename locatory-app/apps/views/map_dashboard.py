import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import flask
from flask import Response
from io import StringIO
from apps.user.customer import Customer
from dash.dependencies import Input, Output, State
from app import app, server
from apps.config.constants import brazil_state_code_map, mapbox_access_token

select_country_div = html.Div([
    html.Label(["Select Country",
                dcc.Checklist(
                    id="country_checkbox",
                    options=[

                    ],
                    value=['Brazil'],
                    labelStyle={'display': 'inline-block'}
                ),
                ],
               style={'display': 'none'}, id="country_checkbox_component"
               ),

])

select_state_div = html.Div([
    html.Label(["Select State",
                dcc.Dropdown(
                    id="state_dropdown",
                    options=[

                    ],
                    value=[],
                    multi=True,
                ),
                ],
               style={'display': 'none'}, id="state_dropdown_component"
               ),
])

select_city_div = html.Div([
    html.Label(["Select City",
                dcc.Dropdown(
                    id="city_dropdown",
                    options=[
                    ],
                    value=[],
                    multi=True,
                ),
                ],
               style={'display': 'none'}, id="city_dropdown_component"
               ),
])

select_gender_div = html.Div([
    html.Label(["Select Gender",
                dcc.Checklist(
                    id="gender_checkbox",
                    options=[

                    ],
                    value=['Male'],
                    labelStyle={'display': 'inline-block'}
                ),
                ],
               style={'display': 'none'}, id="gender_checkbox_component"
               ),
])

select_age_range_div = html.Div([
    html.Label(["Select Age",
                dcc.RangeSlider(
                    id='age-range-slider',
                    step=1,
                    vertical=True,
                    verticalHeight=210

                ),
                html.Div(id='output-container-range-slider-age', style={'textAlign': 'center'})
                ],
               style={'display': 'none'}, id="age-range-slider_component"
               ),
])

select_income_range_div = html.Div([
    html.Label(["Select Income Range",
                dcc.RangeSlider(
                    id='income-range-slider',
                    step=1000,
                    vertical=True,
                    verticalHeight=210
                ),
                html.Div(id='output-container-range-slider-income', style={'textAlign': 'center'})
                ],
               style={'display': 'none'}, id="income-range-slider_component"
               ),
])

layout = dbc.Container([
    html.H2('Map Dashboard'),
    html.Hr(),
    html.Div([

        dbc.Button('Demographic Filters', color='primary', block=True, id="demographic_filter_button"),

        html.Div([

            dbc.Row(
                select_country_div,
            ),
            dbc.Row(
                select_state_div
                ,
            ),
            html.Br(),
            dbc.Row(
                select_city_div,
            ),
            dbc.Row(
                select_gender_div,
            ),
            html.Br(),
            dbc.Row([
                dbc.Col(select_age_range_div, width="6"),
                dbc.Col(select_income_range_div, width="6"),
            ]
            ),
            dbc.Row(
                dcc.Link('Export Csv', refresh=True, id="export-csv-link", href="/map_dashboard/exportCsv")
            )

        ], style={
            'position': 'fixed',
            'zIndex': 2147483647,
            'top': '200px',
            'left': '270px',
            'margin': 0,
            'padding': 0,
            'width': '400px',
            'height': '200px',
            'display': 'block',
        }, id='demographic_navi'),
    ], style={
        'position': 'absolute',
        'zIndex': 35,
        'top': '140px',
        'left': '250px',
        'margin': 0,
        'padding': 0,
        'width': '120px',
        'height': '100px'}, id="demographic_filters_div"
    ),
    # map
    html.Div([
        dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True},
                  # style={'padding-bottom': '2px', 'height': '100vh'},
                  style={'width': '120vw', 'height': '115vh'}
                  )
    ], style={'zIndex': 1, 'position': 'absolute', 'top': '0', 'left': '0', 'marginLeft': '-80px',
              'marginTop': '-8px'})
], className="mt-4")


@app.callback(
    [Output(component_id='country_checkbox_component', component_property='style'),
     Output(component_id='gender_checkbox_component', component_property='style'),
     Output(component_id='state_dropdown_component', component_property='style'),
     Output(component_id='city_dropdown_component', component_property='style'),
     Output(component_id='age-range-slider_component', component_property='style'),
     Output(component_id='income-range-slider_component', component_property='style')
     ],
    [Input(component_id='demographic_filter_button', component_property='n_clicks')])
def show_hide_demographic_filters_element(click_value):
    # On-load
    if click_value is None:
        return [{'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'},
                {'display': 'none'}]
    # Show drop-down on even number of clicks
    elif (click_value % 2) == 0:
        return [{'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'},
                {'display': 'none'}]
    # Show drop-down on odd number of clicks
    else:
        return [{'display': 'block'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'},
                {'display': 'block'}, {'display': 'block'}]


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
    print(f"options", value)
    customer = Customer()
    customer_df = customer.get_customer_dataframe()
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
    print(f"options", value)
    customer = Customer()
    customer_df = customer.get_customer_dataframe()
    unique_cities = customer_df.loc[customer_df['customer_state'].isin(value)]['customer_city'].unique()
    return [
               {'label': f"{key}", 'value': key} for key in unique_cities
           ], unique_cities


@app.callback(Output('graph', 'figure'), Output('export-csv-link', 'href'),
              [Input('gender_checkbox', 'value'), Input('age-range-slider', 'value'),
               Input('income-range-slider', 'value'), Input('country_checkbox', 'value'),
               Input('state_dropdown', 'value')],
              )
def update_fig(gender_values, age_range, income_range, countries, states):
    print(age_range, gender_values, income_range, countries, states)
    export_csv_link = f"/map_dashboard/exportCsv?countries={','.join(countries)}" \
                      f"&states={','.join(states)}" \
                      f"&gender_values={','.join(gender_values)}" \
                      f"&income_range={','.join([str(v) for v in income_range])}" \
                      f"&age_range={','.join([str(v) for v in age_range])}"
    customer = Customer()
    customer_df = customer.get_customer_dataframe()
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
           }, export_csv_link


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

        customer_df = customer.get_customer_dataframe()
        country_checkbox_options = [{'label': key, 'value': key} for key in
                                    sorted(customer_df['customer_country'].unique())]
        gender_checkbox_options = [{'label': key, 'value': key} for key in sorted(customer_df['gender'].unique())]
        age_range_slider_min = customer_df['age'].min()
        age_range_slider_max = customer_df['age'].max()
        age_range_slider_value = [customer_df['age'].min(), customer_df['age'].min() + 3]
        age_range_slider_marks = {int(key): {'label': f"{key}"} for key in range(0, customer_df['age'].max() + 1, 5)}
        income_range_slider_min = customer_df['income'].min()
        income_range_slider_max = customer_df['income'].max()
        income_range_slider_value = [customer_df['income'].min(), customer_df['income'].min() + 5000]
        income_range_slider_marks = {int(key): {'label': f"{key}"} for key in
                                     range(0, customer_df['income'].max() + 1, 5000)}

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


@server.route('/map_dashboard/exportCsv')
def download_csv():
    print('download_csv', flask.request.args)
    customer = Customer()
    df = customer.get_customer_dataframe()
    countries = flask.request.args.get('countries').split(',')
    states = flask.request.args.get('states').split(',')
    gender_values = flask.request.args.get('gender_values').split(',')
    age_range = flask.request.args.get('age_range').split(',')
    income_range = flask.request.args.get('income_range').split(',')

    if countries is not None:
        df = df.loc[df['customer_country'].isin(countries)]
    if states is not None:
        df = df.loc[df['customer_state'].isin(states)]
    if gender_values is not None:
        df = df.loc[df['gender'].isin(gender_values)]
    if age_range is not None and len(age_range) == 2:
        df = df.loc[(df['age'] >= int(age_range[0])) & (df['age'] <= int(age_range[1]))]
    if income_range is not None and len(income_range) == 2:
        df = df.loc[(df['income'] >= int(income_range[0])) & (df['income'] <= int(income_range[1]))]

    if 'customer_id' in df.columns:
        df = df.drop(columns=['customer_id'])

    return Response(
        df.to_csv(index=False),
        mimetype="text/csv",
        headers={"Content-disposition":
                     "attachment; filename=customers.csv"})
    # return send_file(strIO,
    #                  mimetype='text/csv',
    #                  attachment_filename='downloadFile.csv',
    #                  as_attachment=True)
