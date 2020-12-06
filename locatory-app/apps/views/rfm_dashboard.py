import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from apps.db_query.customer import Customer
from apps.rfm.rfm import RFMData
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
from app import app, server
import numpy as np
import urllib.parse as urlparse
from urllib.parse import parse_qs
import flask
from flask import Response
from apps.config.constants import brazil_state_code_map, mapbox_access_token, default_object_id

"""
This is the main Python file for the RFM segmentation dashboard
"""


def fetch_object_id(href):
    """
    This method fetches the object id from the given href

    """
    # Parse url
    parsed = urlparse.urlparse(href)

    # Check if no params are passed
    if len(parse_qs(parsed.query)) == 0:
        # Assign default parameters object
        object_id = default_object_id
    else:
        object_id = parse_qs(parsed.query)['id'][0]

    return object_id


def reduce_dataframe_on_dropdown_options(df, dropdown, column_name):
    """
        This method condenses the dataframe based on given dropdown option and column name

    """

    if not dropdown:
        current_df = df
    else:
        # Condensing dataframe based on R value
        current_df = df.loc[df[column_name].isin(dropdown)]

    return current_df


def generate_csv_link(dropdown_temporal_filter, dropdown_r_filter, dropdown_f_filter, dropdown_m_filter, dropdown_state,
                      dropdown_city, checkbox_gender,
                      object_id):
    """
        This method returns the csv link with parameter name & value pairs

    """

    # Get a copy of dropdown_r_filter,dropdown_f_filter,dropdown_m_filter values
    r_val = dropdown_r_filter
    f_val = dropdown_f_filter
    m_val = dropdown_m_filter

    # Exceptional case to handle r,f,m values
    if r_val == 0 or len(r_val) == 0:
        r_val = [0]

    if f_val == 0 or len(f_val) == 0:
        f_val = [0]

    if m_val == 0 or len(m_val) == 0:
        m_val = [0]

    # Attach parameter-value pairs to the csv link
    export_csv = f"/other_dashboard/exportMyCsv?states={','.join(dropdown_state)}" \
                 f"&city={','.join(dropdown_city)}" \
                 f"&gender_value={','.join(checkbox_gender)}" \
                 f"&temporal_value={str(dropdown_temporal_filter)}" \
                 f"&r_value={','.join([str(v) for v in r_val])}" \
                 f"&f_value={','.join([str(v) for v in f_val])}" \
                 f"&m_value={','.join([str(v) for v in m_val])}" \
                 f"&object_id={object_id}"

    return export_csv


def generate_r_label(customer_df, rfm_model):
    """
        This method does 2 tasks:
        1) Maps the customers in customer data frame and RFM model
        2) Creates a new column r with values taken from the RFM model

    """

    # Get list of customers with different R scores and Update r label
    for item in rfm_model.iloc[0]["r_keys"]:
        val = "R_score" + item
        customer_df.loc[customer_df["customer_id"].isin(
            rfm_model.loc[0][val]), 'r'] = int(item)

    return customer_df


def generate_rfm_columns(customer_df, rfm_model):
    """
        This method does 4 tasks:
        1) Maps the customers in customer data frame and RFM model
        2) Creates a new columns f with F-score values taken from the RFM model
        3) Creates a new column m with M-score values taken from the RFM model
        4) Creates a new column rfm with RFM-label values taken from the RFM model

    """

    # Get list of customers with different F,M scores and Update f,m label
    for i in range(rfm_model['segment_count'].item()):
        j = i + 1
        f_var_name = "F_score" + str(j)
        customer_df.loc[customer_df["customer_id"].isin(
            rfm_model.loc[0][f_var_name]), 'f'] = j

        m_score_name = "M_score" + str(j)
        customer_df.loc[customer_df["customer_id"].isin(
            rfm_model.loc[0][m_score_name]), 'm'] = j

        rfm_name = "segment_" + chr(65 + i)
        customer_df.loc[customer_df["customer_id"].isin(
            rfm_model.loc[0][rfm_name]), 'rfm'] = chr(65 + i)

    return customer_df


def initialize_column_with_nan(customer_df, column_name):
    """
            This method does initializes the column of a dataframe with nan

    """
    # Initialize labels as 1
    customer_df[column_name] = np.nan

    return customer_df


layout = html.Div([
    html.Div([
        dbc.Button('Demographic Filters', color='primary', block=True, id="demo_button"),
        html.Div([
            html.Label(["Select State",
                        dcc.Dropdown(
                            id="dropdown_state",
                            options=[
                            ],
                            value=[],
                            multi=True,
                        ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="dropdown_state_component"
                       ),
            html.Label(["Select City",
                        dcc.Dropdown(
                            id="dropdown_city",
                            options=[
                            ],
                            value=[],
                            multi=True,
                        ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="dropdown_city_component"
                       ),
            html.Label(["Select Gender",
                        dcc.Checklist(
                            id="checkbox_gender",
                            options=[

                            ],
                            value=[],
                            labelStyle={'display': 'inline-block'}
                        ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="checkbox_gender_component"
                       ),
        ], style={
            'position': 'fixed',
            'zIndex': 2147483647,
            'top': '200px',
            'left': '250px',
            'margin': 0,
            'padding': 0,
            'width': '120px',
            'height': '100px',
            'display': 'block',
        }, id='navi'),
    ]
        , style={
            'position': 'absolute',
            'zIndex': 35,
            'top': '140px',
            'left': '250px',
            'margin': 0,
            'padding': 0,
            'width': '120px',
            'height': '100px'}, id="demodiv",
    ),

    html.Div([
        dcc.Link('Export Csv', refresh=True, id="export-csv", href="/other_dashboard/exportMyCsv")
    ], style={
        'position': 'absolute',
        'zIndex': 35,
        'top': '150px',
        'left': '150px',
        'margin': 0,
        'padding': 0,
        'width': '120px',
        'height': '100px'}, id="export_div"
    ),

    html.Div([

        dbc.Button('Algorithm Filters', color='primary', block=True, id="button"),

        html.Div([

            html.Label(["Temporal Filter",
                        dcc.Dropdown(id="dropdown_temporal_filter", value=0, clearable=False
                                     # , style={'color': 'blue', 'backgroundColor': 'blue'}
                                     ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'},
                       id="dropdown_temporal_filter_component"
                       ),

            html.Label(["Select R value",
                        dcc.Dropdown(id="dropdown_r_filter", value=0,
                                     options=[{"label": "value: 1", "value": 1},
                                              {"label": "value: 2", "value": 2},
                                              {"label": "value: 3", "value": 3},
                                              {"label": "value: 4", "value": 4},
                                              {"label": "value: 5", "value": 5}], multi=True
                                     # , style={'color': 'blue', 'backgroundColor': 'blue'}
                                     ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="dropdown_r_filter_component"
                       ),

            html.Label(["Select F value",
                        dcc.Dropdown(id="dropdown_f_filter", value=0, multi=True
                                     # , style={'color': 'blue', 'backgroundColor': 'blue'}
                                     ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="dropdown_f_filter_component"
                       ),

            html.Label(["Select M value",
                        dcc.Dropdown(id="dropdown_m_filter", value=0, multi=True
                                     # , style={'color': 'blue', 'backgroundColor': 'blue'}
                                     ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="dropdown_m_filter_component"
                       ),
        ], style={
            'position': 'fixed',
            'zIndex': 2147483647,
            'top': '200px',
            'left': '1200px',
            'margin': 0,
            'padding': 0,
            'width': '120px',
            'height': '100px',
            'display': 'block',
        }, id='navi'),

    ], style={
        'position': 'absolute',
        'zIndex': 35,
        'top': '140px',
        'left': '1200px',
        'margin': 0,
        'padding': 0,
        'width': '120px',
        'height': '100px'}, id="mydiv"),
    html.Div([

        dcc.Graph(id='graph1', config={'displayModeBar': False, 'scrollZoom': True},
                  style={'width': '120vw', 'height': '115vh'}
                  )

    ], style={'zIndex': 1, 'position': 'absolute', 'top': '0', 'left': '0', 'marginLeft': '-80px',
              'marginTop': '-8px'},
        className="infoi"),
], className="my-container")


@app.callback(
    [Output(component_id='dropdown_temporal_filter_component', component_property='style'),
     Output(component_id='dropdown_r_filter_component', component_property='style'),
     Output(component_id='dropdown_f_filter_component', component_property='style'),
     Output(component_id='dropdown_m_filter_component', component_property='style'),
     ],
    [Input(component_id='button', component_property='n_clicks')])
def show_hide_element(click_value):
    # On-load
    if click_value is None:
        return [{'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
                ]
    # Show drop-down on even number of clicks
    elif (click_value % 2) == 0:
        return [{'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
                ]
    # Show drop-down on odd number of clicks
    else:
        return [{'display': 'block'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}
                ]


@app.callback(
    [Output(component_id='dropdown_state_component', component_property='style'),
     Output(component_id='dropdown_city_component', component_property='style'),
     Output(component_id='checkbox_gender_component', component_property='style'),
     ],
    [Input(component_id='demo_button', component_property='n_clicks')])
def show_hide_element(clicks):
    # On-load
    if clicks is None:
        return [{'display': 'none'}, {'display': 'none'}, {'display': 'none'}
                ]
    # Show drop-down on even number of clicks
    elif (clicks % 2) == 0:
        return [{'display': 'none'}, {'display': 'none'}, {'display': 'none'}
                ]
    # Show drop-down on odd number of clicks
    else:
        return [{'display': 'block'}, {'display': 'block'}, {'display': 'block'}
                ]


@app.callback([Output('dropdown_temporal_filter', 'options'), Output('dropdown_r_filter', 'options')],
              [Input('url', 'href')])
def set_dropdown(href):
    if href is not None:

        # Fetching object id from the href
        object_id = fetch_object_id(href)

        # Get list of end dates from MongoDB
        rfm = RFMData()
        end_dates_iso = rfm.get_all_end_dates(object_id)
        # print(end_dates_iso)

        # Parse the end dates iso to get month and year
        period_values = []
        for value in end_dates_iso:
            period_values.append(value.strftime("%b-%Y"))

        # Set dropdown values
        dropdown_values = [dict(label=x, value=i)
                           for i, x in enumerate(period_values)]

        rfm_df = pd.DataFrame(rfm.get_records(object_id))

        dropdown_labels = []
        list_key = rfm_df.iloc[0]["r_keys"]

        for item in list_key:
            value = "value: " + item
            dropdown_labels.append(value)

        dropdown_r_filter_values = [dict(label=x, value=int(list_key[i]))
                                    for i, x in enumerate(dropdown_labels)]

        # print(dropdown_values)
        return dropdown_values, dropdown_r_filter_values


# Set dropdown_f_filter and dropdown_m_filter based on segment_size of object_id
@app.callback([Output('dropdown_f_filter', 'options'), Output('dropdown_m_filter', 'options')], [Input('url', 'href')])
def set_fm_dropdown_values(href):
    if href is not None:

        # Fetching object id from the href
        object_id = fetch_object_id(href)

        rfm = RFMData()

        # Get RFM model size:
        segment_size = rfm.get_segment_size(object_id)

        dropdown_labels = []
        for i in range(1, segment_size + 1):
            value = "value: " + str(i)
            dropdown_labels.append(value)

        dropdown_values = [dict(label=x, value=i + 1)
                           for i, x in enumerate(dropdown_labels)]

        return dropdown_values, dropdown_values


# Setting graph and state dropdown
@app.callback(Output('graph1', 'figure'), Output('export-csv', 'href'), [Input('dropdown_temporal_filter', 'value'),
                                                                         Input('dropdown_r_filter', 'value'),
                                                                         Input('dropdown_f_filter', 'value'),
                                                                         Input('dropdown_m_filter', 'value'),
                                                                         Input('dropdown_state', 'value'),
                                                                         Input('dropdown_city', 'value'),
                                                                         Input('checkbox_gender', 'value'),
                                                                         Input('url', 'href')]
              )
def update_fig(dropdown_temporal_filter, dropdown_r_filter, dropdown_f_filter, dropdown_m_filter, dropdown_state,
               dropdown_city, checkbox_gender, href):
    if href is not None:

        # Fetching object id from the href
        object_id = fetch_object_id(href)

        # Append name-value pairs to the export csv link
        export_csv = generate_csv_link(dropdown_temporal_filter, dropdown_r_filter, dropdown_f_filter,
                                       dropdown_m_filter, dropdown_state, dropdown_city,
                                       checkbox_gender, object_id)

        # Create rfm object
        rfm = RFMData()

        # Should make a call in maps not here
        rfm_model = pd.DataFrame(rfm.get_records(object_id))

        # Get customers data and append r, f, m, and rfm
        customer = Customer()

        # Get customer data
        customer_df = pd.DataFrame(customer.get_customer_data())

        # Initialize rfm columns with nan
        customer_df = initialize_column_with_nan(customer_df, "r")
        customer_df = initialize_column_with_nan(customer_df, "f")
        customer_df = initialize_column_with_nan(customer_df, "m")
        customer_df = initialize_column_with_nan(customer_df, "rfm")

        # Retrieve that particular row
        rfm_model = rfm_model.iloc[[dropdown_temporal_filter]]
        rfm_model.reset_index(inplace=True)

        # Create a new column r with the r scores
        customer_df = generate_r_label(customer_df, rfm_model)

        # Creates three new columns: 1) f with f scores 2) m with m scores 3) rfm column with combined rfm label values
        customer_df = generate_rfm_columns(customer_df, rfm_model)

        # Remove customers with no label
        customer_df = customer_df[customer_df['rfm'].notna()]
        customer_df = customer_df.sort_values(by=["rfm"])
        customer_df.reset_index(inplace=True)

        # Define a list of colors for each segment
        color_val = {'A': 'green', 'B': 'gray', 'C': 'blue', 'D': 'orange', 'E': 'yellow', 'F': 'brown', 'G': 'pink',
                     'H': 'purple', 'I': 'teal', 'J': 'red'}

        # Reduce the dataframe based on R value
        current_df = reduce_dataframe_on_dropdown_options(customer_df, dropdown_r_filter, "r")

        # Reduce the dataframe based on F value
        current_df = reduce_dataframe_on_dropdown_options(current_df, dropdown_f_filter, "f")

        # Reduce the dataframe based on M value
        current_df = reduce_dataframe_on_dropdown_options(current_df, dropdown_m_filter, "m")

        # Reduce the dataframe based on state value
        current_df = reduce_dataframe_on_dropdown_options(current_df, dropdown_state, "customer_state")

        # Reduce the dataframe based on city value
        current_df = reduce_dataframe_on_dropdown_options(current_df, dropdown_city, "customer_city")

        # Reduce the dataframe based on gender value
        current_df = reduce_dataframe_on_dropdown_options(current_df, checkbox_gender, "gender")

        locations = []
        for lbl in current_df['rfm'].unique():
            # Different classes
            new_df = current_df.loc[current_df["rfm"] == lbl]
            current_trace_name = "Class-" + lbl + " " + str(len(new_df))

            locations.append(go.Scattermapbox(
                lon=new_df['long'],
                lat=new_df['lat'],
                name=current_trace_name,
                mode='markers',
                marker=dict(color=color_val[lbl], size=6),
                showlegend=True,
                text=new_df[["age", "gender", "income"]]
            ))

        return {
                   'data': locations,
                   'layout': go.Layout(
                       uirevision='foo',
                       clickmode='event+select',
                       hovermode='closest',
                       hoverdistance=2,
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
                       legend=dict(
                           yanchor="top",
                           y=0.7,
                           xanchor="left",
                           x=0,
                           traceorder='normal',
                           font=dict(
                               family="Courier",
                               color="black",
                               size=12),
                           bgcolor="LightSteelBlue",
                           bordercolor="Black",
                           borderwidth=2,
                           title_font_family="Times New Roman",

                       ),
                   )
               }, export_csv


@app.callback(Output('dropdown_state', 'options'),
              [Input('dropdown_temporal_filter', 'value'), Input('dropdown_r_filter', 'value'),
               Input('dropdown_f_filter', 'value'),
               Input('dropdown_m_filter', 'value'), Input('url', 'href')])
def update_state_dropdown(dropdown_temporal_filter, dropdown_r_filter, dropdown_f_filter, dropdown_m_filter, href):
    if href is not None:
        # Fetching object id from the href
        object_id = fetch_object_id(href)

        # Create rfm object
        rfm = RFMData()

        # Should make a call in maps not here
        rfm_model = pd.DataFrame(rfm.get_records(object_id))

        # Get customers data and append r, f, m, and rfm
        customer = Customer()

        # Get customer data
        customer_df = pd.DataFrame(customer.get_customer_data())

        # Initialize rfm columns with nan
        customer_df = initialize_column_with_nan(customer_df, "r")
        customer_df = initialize_column_with_nan(customer_df, "f")
        customer_df = initialize_column_with_nan(customer_df, "m")
        customer_df = initialize_column_with_nan(customer_df, "rfm")

        # Retrieve that particular row
        rfm_model = rfm_model.iloc[[dropdown_temporal_filter]]
        rfm_model.reset_index(inplace=True)

        # Create a new column r with the r scores
        customer_df = generate_r_label(customer_df, rfm_model)

        # Creates three new columns: 1) f with f scores 2) m with m scores 3) rfm column with combined rfm label values
        customer_df = generate_rfm_columns(customer_df, rfm_model)

        # Remove customers with no label
        customer_df = customer_df[customer_df['rfm'].notna()]
        customer_df = customer_df.sort_values(by=["rfm"])
        customer_df.reset_index(inplace=True)

        # Reduce the dataframe based on R value
        current_df = reduce_dataframe_on_dropdown_options(customer_df, dropdown_r_filter, "r")

        # Reduce the dataframe based on F value
        current_df = reduce_dataframe_on_dropdown_options(current_df, dropdown_f_filter, "f")

        # Reduce the dataframe based on M value
        current_df = reduce_dataframe_on_dropdown_options(current_df, dropdown_m_filter, "m")

        # Based on current_df update return the state options
        states = sorted(current_df['customer_state'].unique())

        return [
            {'label': f"{brazil_state_code_map[key]}", 'value': key} for key in states
        ]


@app.callback(
    Output('dropdown_city', 'options'),
    [Input('dropdown_state', 'value'), Input('dropdown_temporal_filter', 'value'), Input('dropdown_r_filter', 'value'),
     Input('dropdown_f_filter', 'value'), Input('dropdown_m_filter', 'value'), Input('url', 'href')],
)
def update_city_dropdown(dropdown_state, dropdown_temporal_filter, dropdown_r_filter, dropdown_f_filter,
                         dropdown_m_filter, href):
    if href is not None:

        # Fetching object id from the href
        object_id = fetch_object_id(href)

        # Create rfm object
        rfm = RFMData()

        # Should make a call in maps not here
        rfm_model = pd.DataFrame(rfm.get_records(object_id))

        # Get customers data and append r, f, m, and rfm
        customer = Customer()

        # Get customer data
        customer_df = pd.DataFrame(customer.get_customer_data())

        # Initialize rfm columns with nan
        customer_df = initialize_column_with_nan(customer_df, "r")
        customer_df = initialize_column_with_nan(customer_df, "f")
        customer_df = initialize_column_with_nan(customer_df, "m")
        customer_df = initialize_column_with_nan(customer_df, "rfm")

        # Retrieve that particular row
        rfm_model = rfm_model.iloc[[dropdown_temporal_filter]]
        rfm_model.reset_index(inplace=True)

        # Create a new column r with the r scores
        customer_df = generate_r_label(customer_df, rfm_model)

        # Creates three new columns: 1) f with f scores 2) m with m scores 3) rfm column with combined rfm label values
        customer_df = generate_rfm_columns(customer_df, rfm_model)

        # Remove customers with no label
        customer_df = customer_df[customer_df['rfm'].notna()]
        customer_df = customer_df.sort_values(by=["rfm"])
        customer_df.reset_index(inplace=True)

        # Reduce the dataframe based on R value
        current_df = reduce_dataframe_on_dropdown_options(customer_df, dropdown_r_filter, "r")

        # Reduce the dataframe based on F value
        current_df = reduce_dataframe_on_dropdown_options(current_df, dropdown_f_filter, "f")

        # Reduce the dataframe based on M value
        current_df = reduce_dataframe_on_dropdown_options(current_df, dropdown_m_filter, "m")

        # Now retrieve the states based on reduced dataframe
        if dropdown_state == 0 or dropdown_state is None or not dropdown_state:
            cities = current_df['customer_city'].unique()
        else:
            # Get cities based on current state selection
            cities = current_df.loc[current_df['customer_state'].isin(dropdown_state)]['customer_city'].unique()

        return [
            {'label': f"{key}", 'value': key} for key in cities
        ]


@app.callback(
    Output('checkbox_gender', 'options'),
    [Input('dropdown_temporal_filter', 'value'), Input('dropdown_r_filter', 'value'),
     Input('dropdown_f_filter', 'value'), Input('dropdown_m_filter', 'value'), Input('dropdown_state', 'value'),
     Input('dropdown_city', 'value'), Input('url', 'href')],
)
def update_gender_checkbox(dropdown_temporal_filter, dropdown_r_filter, dropdown_f_filter, dropdown_m_filter,
                           dropdown_state, dropdown_city, href):
    if href is not None:
        # Fetching object id from the href
        object_id = fetch_object_id(href)

        # Create rfm object
        rfm = RFMData()

        # Should make a call in maps not here
        rfm_model = pd.DataFrame(rfm.get_records(object_id))

        # Get customers data and append r, f, m, and rfm
        customer = Customer()

        # Get customer data
        customer_df = pd.DataFrame(customer.get_customer_data())

        # Initialize rfm columns with nan
        customer_df = initialize_column_with_nan(customer_df, "r")
        customer_df = initialize_column_with_nan(customer_df, "f")
        customer_df = initialize_column_with_nan(customer_df, "m")
        customer_df = initialize_column_with_nan(customer_df, "rfm")

        # Retrieve that particular row
        rfm_model = rfm_model.iloc[[dropdown_temporal_filter]]
        rfm_model.reset_index(inplace=True)

        # Create a new column r with the r scores
        customer_df = generate_r_label(customer_df, rfm_model)

        # Creates three new columns: 1) f with f scores 2) m with m scores 3) rfm column with combined rfm label values
        customer_df = generate_rfm_columns(customer_df, rfm_model)

        # Remove customers with no label
        customer_df = customer_df[customer_df['rfm'].notna()]
        customer_df = customer_df.sort_values(by=["rfm"])
        customer_df.reset_index(inplace=True)

        # Reduce the dataframe based on R value
        current_df = reduce_dataframe_on_dropdown_options(customer_df, dropdown_r_filter, "r")

        # Reduce the dataframe based on F value
        current_df = reduce_dataframe_on_dropdown_options(current_df, dropdown_f_filter, "f")

        # Reduce the dataframe based on M value
        current_df = reduce_dataframe_on_dropdown_options(current_df, dropdown_m_filter, "m")

        # Reduce the dataframe based on state value
        current_df = reduce_dataframe_on_dropdown_options(current_df, dropdown_state, "customer_state")

        # Reduce the dataframe based on city value
        current_df = reduce_dataframe_on_dropdown_options(current_df, dropdown_city, "customer_city")

        gender_options = [{'label': key, 'value': key} for key in sorted(current_df['gender'].unique())]

        return gender_options


# Export csv functionality
@server.route('/other_dashboard/exportMyCsv')
def download_segmented_csv():
    object_id = flask.request.args.get('object_id')
    states = flask.request.args.get('states').split(',')
    cities = flask.request.args.get('city').split(',')
    gender_values = flask.request.args.get('gender_value').split(',')
    temporal_values = flask.request.args.get('temporal_value')
    r_value = flask.request.args.get('r_value').split(',')
    f_value = flask.request.args.get('f_value').split(',')
    m_value = flask.request.args.get('m_value').split(',')

    # Create rfm object
    rfm = RFMData()

    # Should make a call in maps not here
    rfm_model = pd.DataFrame(rfm.get_records(object_id))

    # Get customers data and append r, f, m, and rfm
    customer = Customer()

    # Get customer data
    customer_df = pd.DataFrame(customer.get_customer_data())

    # Initialize rfm columns with nan
    customer_df = initialize_column_with_nan(customer_df, "r")
    customer_df = initialize_column_with_nan(customer_df, "f")
    customer_df = initialize_column_with_nan(customer_df, "m")
    customer_df = initialize_column_with_nan(customer_df, "rfm")

    # Retrieve that particular row
    rfm_model = rfm_model.iloc[[temporal_values]]
    rfm_model.reset_index(inplace=True)

    # Create a new column r with the r scores
    customer_df = generate_r_label(customer_df, rfm_model)

    # Creates three new columns: 1) f with f scores 2) m with m scores 3) rfm column with combined rfm label values
    customer_df = generate_rfm_columns(customer_df, rfm_model)

    # Remove customers with no label
    customer_df = customer_df[customer_df['rfm'].notna()]
    customer_df = customer_df.sort_values(by=["rfm"])
    customer_df.reset_index(inplace=True)

    if not r_value or r_value == ['0']:
        current_df = customer_df
    else:
        # Condensing dataframe based on R value
        current_df = customer_df.loc[customer_df["r"].isin(r_value)]

    if not f_value or f_value == ['0']:
        current_df = current_df
    else:
        # Condensing dataframe based on F value
        current_df = current_df.loc[current_df["f"].isin(f_value)]

    if not m_value or m_value == ['0']:
        current_df = current_df
    else:
        # Condensing dataframe based on M value
        current_df = current_df.loc[current_df["m"].isin(m_value)]

    if not states or '' in states:
        current_df = current_df
    else:
        # Condensing dataframe based on state value
        current_df = current_df.loc[current_df["customer_state"].isin(
            states)]

    if not cities or '' in cities:
        current_df = current_df
    else:
        # Condensing dataframe based on state value
        current_df = current_df.loc[current_df["customer_city"].isin(cities)]

    if not gender_values or '' in gender_values:
        current_df = current_df
    else:
        # Condensing dataframe based on gender value
        current_df = current_df.loc[current_df["gender"].isin(gender_values)]

    return Response(
        current_df.to_csv(index=False),
        mimetype="text/csv",
        headers={"Content-disposition":
                     "attachment; filename=segmented_customers.csv"})
