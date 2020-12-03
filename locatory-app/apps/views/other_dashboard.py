import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from apps.user.customer import Customer
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
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="dropdown5_component"
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
                        dcc.Dropdown(id="dropdown1", value=0, clearable=False
                                     # , style={'color': 'blue', 'backgroundColor': 'blue'}
                                     ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="dropdown1_component"
                       ),

            html.Label(["Select R value",
                        dcc.Dropdown(id="dropdown2", value=0,
                                     options=[{"label": "value: 1", "value": 1},
                                              {"label": "value: 2", "value": 2},
                                              {"label": "value: 3", "value": 3},
                                              {"label": "value: 4", "value": 4},
                                              {"label": "value: 5", "value": 5}], multi=True
                                     # , style={'color': 'blue', 'backgroundColor': 'blue'}
                                     ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="dropdown2_component"
                       ),

            html.Label(["Select F value",
                        dcc.Dropdown(id="dropdown3", value=0, multi=True
                                     # , style={'color': 'blue', 'backgroundColor': 'blue'}
                                     ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="dropdown3_component"
                       ),

            html.Label(["Select M value",
                        dcc.Dropdown(id="dropdown4", value=0, multi=True
                                     # , style={'color': 'blue', 'backgroundColor': 'blue'}
                                     ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="dropdown4_component"
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
    [Output(component_id='dropdown1_component', component_property='style'),
     Output(component_id='dropdown2_component', component_property='style'),
     Output(component_id='dropdown3_component', component_property='style'),
     Output(component_id='dropdown4_component', component_property='style'),
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
    [Output(component_id='dropdown5_component', component_property='style'),
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


@app.callback([Output('dropdown1', 'options'), Output('dropdown2', 'options')], [Input('url', 'href')])
def set_dropdown(href):
    if href is not None:

        # Parse url
        parsed = urlparse.urlparse(href)

        # Check if no params are passed
        if len(parse_qs(parsed.query)) == 0:
            # Assign default parameters object
            object_id = default_object_id
        else:
            object_id = parse_qs(parsed.query)['id'][0]

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

        dropdown2_values = [dict(label=x, value=int(list_key[i]))
                            for i, x in enumerate(dropdown_labels)]

        # print(dropdown_values)
        return dropdown_values, dropdown2_values


# Set dropdown3 and dropdown4 based on segment_size of object_id
@app.callback([Output('dropdown3', 'options'), Output('dropdown4', 'options')], [Input('url', 'href')])
def set_fm_dropdown_values(href):
    if href is not None:

        # Parse url
        parsed = urlparse.urlparse(href)

        # Check if no params are passed
        if len(parse_qs(parsed.query)) == 0:
            # Assign default parameters object
            object_id = default_object_id
        else:
            object_id = parse_qs(parsed.query)['id'][0]

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
@app.callback(Output('graph1', 'figure'), Output('export-csv', 'href'), [Input('dropdown1', 'value'),
                                                                         Input('dropdown2', 'value'),
                                                                         Input('dropdown3', 'value'),
                                                                         Input('dropdown4', 'value'),
                                                                         Input('dropdown_state', 'value'),
                                                                         Input('dropdown_city', 'value'),
                                                                         Input('checkbox_gender', 'value'),
                                                                         Input('url', 'href')]
              )
def update_fig(dropdown1, dropdown2, dropdown3, dropdown4, dropdown_state, dropdown_city, checkbox_gender, href):
    if href is not None:

        # Parse url
        parsed = urlparse.urlparse(href)

        # Check if no params are passed
        if len(parse_qs(parsed.query)) == 0:
            # Assign default parameters object
            object_id = default_object_id
        else:
            object_id = parse_qs(parsed.query)['id'][0]

        # Get a copy of dropdown2,dropdown3,dropdown4 values
        r_val = dropdown2
        f_val = dropdown3
        m_val = dropdown4

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
                     f"&temporal_value={str(dropdown1)}" \
                     f"&r_value={','.join([str(v) for v in r_val])}" \
                     f"&f_value={','.join([str(v) for v in f_val])}" \
                     f"&m_value={','.join([str(v) for v in m_val])}" \
                     f"&object_id={object_id}"

        # Create rfm object
        rfm = RFMData()

        # Should make a call in maps not here
        rfm_model = pd.DataFrame(rfm.get_records(object_id))

        # Get customers data and append r, f, m, and rfm
        customer = Customer()

        # Get customer data
        customer_df = pd.DataFrame(customer.get_customer_data())

        # Initialize labels as 1
        customer_df["r"] = np.nan
        customer_df["f"] = np.nan
        customer_df["m"] = np.nan
        customer_df["rfm"] = np.nan

        # Retrieve that particular row
        rfm_model = rfm_model.iloc[[dropdown1]]
        rfm_model.reset_index(inplace=True)

        # Get list of customers with different R scores and Update r label
        for item in rfm_model.iloc[0]["r_keys"]:
            val = "R_score" + item
            customer_df.loc[customer_df["customer_id"].isin(
                rfm_model.loc[0][val]), 'r'] = int(item)

        # Get list of customers with different F,M scores and Update f,m label
        for i in range(rfm_model['segment_count'].item()):
            j = i + 1
            f_var_name = "F_score" + str(j)
            customer_df.loc[customer_df["customer_id"].isin(
                rfm_model.loc[0][f_var_name]), 'f'] = j

            m_score_name = "M_score" + str(j)
            customer_df.loc[customer_df["customer_id"].isin(
                rfm_model.loc[0][m_score_name]), 'm'] = j

        # Get list of different segmented customers and Update rfm label column
        for i in range(rfm_model['segment_count'].item()):
            val = "segment_" + chr(65 + i)
            customer_df.loc[customer_df["customer_id"].isin(
                rfm_model.loc[0][val]), 'rfm'] = chr(65 + i)

        # Remove customers with no label
        customer_df = customer_df[customer_df['rfm'].notna()]
        customer_df = customer_df.sort_values(by=["rfm"])
        customer_df.reset_index(inplace=True)

        # Define a list of colors
        # Index0 - Empty, Green - class A , Red - class B, Blue - class C, Orange - class D, Yellow - class E
        color_val = {'A': 'green',
                     'B': 'gray',
                     'C': 'blue',
                     'D': 'orange',
                     'E': 'yellow', 'F': 'brown', 'G': 'pink', 'H': 'purple', 'I': 'teal', 'J': 'red'}

        if dropdown2 == 0 or dropdown2 is None or not dropdown2:
            current_df = customer_df
        else:
            # Condensing dataframe based on R value
            current_df = customer_df.loc[customer_df["r"].isin(dropdown2)]

        if dropdown3 == 0 or dropdown3 is None or not dropdown3:
            current_df = current_df
        else:
            # Condensing dataframe based on F value
            current_df = current_df.loc[current_df["f"].isin(dropdown3)]

        if dropdown4 == 0 or dropdown4 is None or not dropdown4:
            current_df = current_df
        else:
            # Condensing dataframe based on M value
            current_df = current_df.loc[current_df["m"].isin(dropdown4)]

        if dropdown_state == 0 or dropdown_state is None or not dropdown_state:
            current_df = current_df
        else:
            # Condensing dataframe based on state value
            current_df = current_df.loc[current_df["customer_state"].isin(
                dropdown_state)]

        if dropdown_city == 0 or dropdown_city is None or not dropdown_city:
            current_df = current_df
        else:
            # Condensing dataframe based on state value
            current_df = current_df.loc[current_df["customer_city"].isin(dropdown_city)]

        if checkbox_gender == 0 or checkbox_gender is None or not checkbox_gender:
            current_df = current_df
        else:
            # Condensing dataframe based on gender value
            current_df = current_df.loc[current_df["gender"].isin(checkbox_gender)]

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
              [Input('dropdown1', 'value'), Input('dropdown2', 'value'), Input('dropdown3', 'value'),
               Input('dropdown4', 'value'), Input('url', 'href')])
def update_state_dropdown(dropdown1, dropdown2, dropdown3, dropdown4, href):
    if href is not None:

        # Parse url
        parsed = urlparse.urlparse(href)

        # Check if no params are passed
        if len(parse_qs(parsed.query)) == 0:
            # Assign default parameters object
            object_id = default_object_id
        else:
            object_id = parse_qs(parsed.query)['id'][0]

        # Create rfm object
        rfm = RFMData()

        # Should make a call in maps not here
        rfm_model = pd.DataFrame(rfm.get_records(object_id))

        # Get customers data and append r, f, m, and rfm
        customer = Customer()

        # Get customer data
        customer_df = pd.DataFrame(customer.get_customer_data())

        # Initialize labels as 1
        customer_df["r"] = np.nan
        customer_df["f"] = np.nan
        customer_df["m"] = np.nan
        customer_df["rfm"] = np.nan

        # Retrieve that particular row
        rfm_model = rfm_model.iloc[[dropdown1]]
        rfm_model.reset_index(inplace=True)

        # Get list of customers with different R scores and Update r label
        for item in rfm_model.iloc[0]["r_keys"]:
            val = "R_score" + item
            customer_df.loc[customer_df["customer_id"].isin(
                rfm_model.loc[0][val]), 'r'] = int(item)

        # Get list of customers with different F,M scores and Update f,m label
        for i in range(rfm_model['segment_count'].item()):
            j = i + 1
            f_var_name = "F_score" + str(j)
            customer_df.loc[customer_df["customer_id"].isin(
                rfm_model.loc[0][f_var_name]), 'f'] = j

            m_score_name = "M_score" + str(j)
            customer_df.loc[customer_df["customer_id"].isin(
                rfm_model.loc[0][m_score_name]), 'm'] = j

        # Get list of different segmented customers and Update rfm label column
        for i in range(rfm_model['segment_count'].item()):
            val = "segment_" + chr(65 + i)
            customer_df.loc[customer_df["customer_id"].isin(
                rfm_model.loc[0][val]), 'rfm'] = chr(65 + i)

        # Remove customers with no label
        customer_df = customer_df[customer_df['rfm'].notna()]
        customer_df = customer_df.sort_values(by=["rfm"])
        customer_df.reset_index(inplace=True)

        if dropdown2 == 0 or dropdown2 is None or not dropdown2:
            current_df = customer_df
        else:
            # Condensing dataframe based on R value
            current_df = customer_df.loc[customer_df["r"].isin(dropdown2)]

        if dropdown3 == 0 or dropdown3 is None or not dropdown3:
            current_df = current_df
        else:
            # Condensing dataframe based on F value
            current_df = current_df.loc[current_df["f"].isin(dropdown3)]

        if dropdown4 == 0 or dropdown4 is None or not dropdown4:
            current_df = current_df
        else:
            # Condensing dataframe based on M value
            current_df = current_df.loc[current_df["m"].isin(dropdown4)]

        # Based on current_df update return the state options
        states = sorted(current_df['customer_state'].unique())

        return [
            {'label': f"{brazil_state_code_map[key]}", 'value': key} for key in states
        ]


@app.callback(
    Output('dropdown_city', 'options'),
    [Input('dropdown_state', 'value'), Input('dropdown1', 'value'), Input('dropdown2', 'value'),
     Input('dropdown3', 'value'), Input('dropdown4', 'value'), Input('url', 'href')],
)
def update_city_dropdown(dropdown_state, dropdown1, dropdown2, dropdown3, dropdown4, href):
    if href is not None:

        # Parse url
        parsed = urlparse.urlparse(href)

        # Check if no params are passed
        if len(parse_qs(parsed.query)) == 0:
            # Assign default parameters object
            object_id = default_object_id
        else:
            object_id = parse_qs(parsed.query)['id'][0]

        # Create rfm object
        rfm = RFMData()

        # Should make a call in maps not here
        rfm_model = pd.DataFrame(rfm.get_records(object_id))

        # Get customers data and append r, f, m, and rfm
        customer = Customer()

        # Get customer data
        customer_df = pd.DataFrame(customer.get_customer_data())

        # Initialize labels as 1
        customer_df["r"] = np.nan
        customer_df["f"] = np.nan
        customer_df["m"] = np.nan
        customer_df["rfm"] = np.nan

        # Retrieve that particular row
        rfm_model = rfm_model.iloc[[dropdown1]]
        rfm_model.reset_index(inplace=True)

        # Get list of customers with different R scores and Update r label
        for item in rfm_model.iloc[0]["r_keys"]:
            val = "R_score" + item
            customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0][val]), 'r'] = int(item)

        # Get list of customers with different F,M scores and Update f,m label
        for i in range(rfm_model['segment_count'].item()):
            j = i + 1
            f_var_name = "F_score" + str(j)
            customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0][f_var_name]), 'f'] = j

            m_score_name = "M_score" + str(j)
            customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0][m_score_name]), 'm'] = j

        # Get list of different segmented customers and Update rfm label column
        for i in range(rfm_model['segment_count'].item()):
            val = "segment_" + chr(65 + i)
            customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0][val]), 'rfm'] = chr(65 + i)

        # Remove customers with no label
        customer_df = customer_df[customer_df['rfm'].notna()]
        customer_df = customer_df.sort_values(by=["rfm"])
        customer_df.reset_index(inplace=True)

        if dropdown2 == 0 or dropdown2 is None or not dropdown2:
            current_df = customer_df
        else:
            # Condensing dataframe based on R value
            current_df = customer_df.loc[customer_df["r"].isin(dropdown2)]

        if dropdown3 == 0 or dropdown3 is None or not dropdown3:
            current_df = current_df
        else:
            # Condensing dataframe based on F value
            current_df = current_df.loc[current_df["f"].isin(dropdown3)]

        if dropdown4 == 0 or dropdown4 is None or not dropdown4:
            current_df = current_df
        else:
            # Condensing dataframe based on M value
            current_df = current_df.loc[current_df["m"].isin(dropdown4)]

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
    [Input('dropdown1', 'value'), Input('dropdown2', 'value'),
     Input('dropdown3', 'value'), Input('dropdown4', 'value'), Input('dropdown_state', 'value'),
     Input('dropdown_city', 'value'), Input('url', 'href')],
)
def update_gender_checkbox(dropdown1, dropdown2, dropdown3, dropdown4, dropdown_state, dropdown_city, href):
    if href is not None:

        # Parse url
        parsed = urlparse.urlparse(href)

        # Check if no params are passed
        if len(parse_qs(parsed.query)) == 0:
            # Assign default parameters object
            object_id = default_object_id
        else:
            object_id = parse_qs(parsed.query)['id'][0]

        # Create rfm object
        rfm = RFMData()

        # Should make a call in maps not here
        rfm_model = pd.DataFrame(rfm.get_records(object_id))

        # Get customers data and append r, f, m, and rfm
        customer = Customer()

        # Get customer data
        customer_df = pd.DataFrame(customer.get_customer_data())

        # Initialize labels as 1
        customer_df["r"] = np.nan
        customer_df["f"] = np.nan
        customer_df["m"] = np.nan
        customer_df["rfm"] = np.nan

        # Retrieve that particular row
        rfm_model = rfm_model.iloc[[dropdown1]]
        rfm_model.reset_index(inplace=True)

        # Get list of customers with different R scores and Update r label
        for item in rfm_model.iloc[0]["r_keys"]:
            val = "R_score" + item
            customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0][val]), 'r'] = int(item)

        # Get list of customers with different F,M scores and Update f,m label
        for i in range(rfm_model['segment_count'].item()):
            j = i + 1
            f_var_name = "F_score" + str(j)
            customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0][f_var_name]), 'f'] = j

            m_score_name = "M_score" + str(j)
            customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0][m_score_name]), 'm'] = j

        # Get list of different segmented customers and Update rfm label column
        for i in range(rfm_model['segment_count'].item()):
            val = "segment_" + chr(65 + i)
            customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0][val]), 'rfm'] = chr(65 + i)

        # Remove customers with no label
        customer_df = customer_df[customer_df['rfm'].notna()]
        customer_df = customer_df.sort_values(by=["rfm"])
        customer_df.reset_index(inplace=True)

        if dropdown2 == 0 or dropdown2 is None or not dropdown2:
            current_df = customer_df
        else:
            # Condensing dataframe based on R value
            current_df = customer_df.loc[customer_df["r"].isin(dropdown2)]

        if dropdown3 == 0 or dropdown3 is None or not dropdown3:
            current_df = current_df
        else:
            # Condensing dataframe based on F value
            current_df = current_df.loc[current_df["f"].isin(dropdown3)]

        if dropdown4 == 0 or dropdown4 is None or not dropdown4:
            current_df = current_df
        else:
            # Condensing dataframe based on M value
            current_df = current_df.loc[current_df["m"].isin(dropdown4)]

        if dropdown_state == 0 or dropdown_state is None or not dropdown_state:
            current_df = current_df
        else:
            # Condensing dataframe based on State value
            current_df = current_df.loc[current_df["customer_state"].isin(dropdown_state)]

        if dropdown_city == 0 or dropdown4 is None or not dropdown4:
            current_df = current_df
        else:
            # Condensing dataframe based on city value
            current_df = current_df.loc[current_df["customer_city"].isin(dropdown_city)]
        gender_options = [{'label': key, 'value': key} for key in sorted(current_df['gender'].unique())]

        return gender_options


# Export csv functionality
@server.route('/other_dashboard/exportMyCsv')
def download_segmented_csv():
    # print('download_csv', flask.request.args)
    # Get all dropdown values
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

    # Initialize labels as 1
    customer_df["r"] = np.nan
    customer_df["f"] = np.nan
    customer_df["m"] = np.nan
    customer_df["rfm"] = np.nan

    # Retrieve that particular row
    rfm_model = rfm_model.iloc[[temporal_values]]
    rfm_model.reset_index(inplace=True)

    # Get list of customers with different R scores and Update r label
    for item in rfm_model.iloc[0]["r_keys"]:
        val = "R_score" + item
        customer_df.loc[customer_df["customer_id"].isin(
            rfm_model.loc[0][val]), 'r'] = int(item)

    # Get list of customers with different F,M scores and Update f,m label
    for i in range(rfm_model['segment_count'].item()):
        j = i + 1
        f_var_name = "F_score" + str(j)
        customer_df.loc[customer_df["customer_id"].isin(
            rfm_model.loc[0][f_var_name]), 'f'] = j

        m_score_name = "M_score" + str(j)
        customer_df.loc[customer_df["customer_id"].isin(
            rfm_model.loc[0][m_score_name]), 'm'] = j

    # Get list of different segmented customers and Update rfm label column
    for i in range(rfm_model['segment_count'].item()):
        val = "segment_" + chr(65 + i)
        customer_df.loc[customer_df["customer_id"].isin(
            rfm_model.loc[0][val]), 'rfm'] = chr(65 + i)

    # Remove customers with no label
    customer_df = customer_df[customer_df['rfm'].notna()]
    customer_df = customer_df.sort_values(by=["rfm"])
    customer_df.reset_index(inplace=True)

    if r_value == 0 or r_value is None or not r_value or r_value == ['0']:
        current_df = customer_df
    else:
        # Condensing dataframe based on R value
        current_df = customer_df.loc[customer_df["r"].isin(r_value)]

    if f_value == 0 or f_value is None or not f_value or f_value == ['0']:
        current_df = current_df
    else:
        # Condensing dataframe based on F value
        current_df = current_df.loc[current_df["f"].isin(f_value)]

    if m_value == 0 or m_value is None or not m_value or m_value == ['0']:
        current_df = current_df
    else:
        # Condensing dataframe based on M value
        current_df = current_df.loc[current_df["m"].isin(m_value)]

    if states == 0 or states is None or not states or '' in states:
        current_df = current_df
    else:
        # Condensing dataframe based on state value
        current_df = current_df.loc[current_df["customer_state"].isin(
            states)]

    if cities == 0 or cities is None or not cities or '' in cities:
        current_df = current_df
    else:
        # Condensing dataframe based on state value
        current_df = current_df.loc[current_df["customer_city"].isin(cities)]

    if gender_values == 0 or gender_values is None or not gender_values or '' in gender_values:
        current_df = current_df
    else:
        # Condensing dataframe based on gender value
        current_df = current_df.loc[current_df["gender"].isin(gender_values)]

    return Response(
        current_df.to_csv(index=False),
        mimetype="text/csv",
        headers={"Content-disposition":
                     "attachment; filename=segmented_customers.csv"})
