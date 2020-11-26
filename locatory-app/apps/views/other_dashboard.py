import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from apps.user.customer import Customer
from apps.rfm.rfm import RFMData
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
from app import app
import numpy as np
import random

# dbc.Container([
#
# # html.H2('Default RFM dashboard'),
# html.Hr(),

# Define RFM object:
dummy_obj = "5fbde042fd6d20542b9edbd5"

layout = html.Div([

    html.H2('RFM '),

    html.Div([

        dbc.Button('Filter Options', color='primary', block=True, id="button"),

        html.Div([

            # dbc.FormGroup([
            # dbc.Row([
            # dbc.Col(
            # dbc.Label("Choose Dataset"),
            html.Label(["Temporal Filter",
                        dcc.Dropdown(id="dropdown1", value=0, clearable=False
                                     # , style={'color': 'blue', 'backgroundColor': 'blue'}
                                     ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="dropdown1_component"
                       ),
            # ),
            # dbc.Col(
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
            # ),
            # dbc.Col(
            html.Label(["Select F value",
                        dcc.Dropdown(id="dropdown3", value=0, multi=True
                                     # , style={'color': 'blue', 'backgroundColor': 'blue'}
                                     ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="dropdown3_component"
                       ),
            # ),

            html.Label(["Select M value",
                        dcc.Dropdown(id="dropdown4", value=0, multi=True
                                     # , style={'color': 'blue', 'backgroundColor': 'blue'}
                                     ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="dropdown4_component"
                       ),
            # ]),
            # ]),
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

    ], style={
        'position': 'absolute',
        'zIndex': 35,
        'top': '140px',
        'left': '250px',
        'margin': 0,
        'padding': 0,
        'width': '100px',
        'height': '100px'}, id="mydiv"),
    html.Div([
        # dbc.Row([
        #     dbc.Col(
        dcc.Graph(id='graph1', config={'displayModeBar': False, 'scrollZoom': True},
                  style={'width': '120vw', 'height': '115vh'}
                  )
        # ),
        # ]),
    ], style={'zIndex': 1, 'position': 'absolute', 'top': '0', 'left': '0', 'marginLeft': '-80px',
              'marginTop': '-8px'},
        className="infoi"),
], className="my-container")


# ], className="mt-4")

@app.callback(
    [Output(component_id='dropdown1_component', component_property='style'),
     Output(component_id='dropdown2_component', component_property='style'),
     Output(component_id='dropdown3_component', component_property='style'),
     Output(component_id='dropdown4_component', component_property='style')],
    [Input(component_id='button', component_property='n_clicks')])
def show_hide_element(click_value):
    # On-load
    if click_value is None:
        return [{'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}]
    # Show drop-down on even number of clicks
    elif (click_value % 2) == 0:
        return [{'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}]
    # Show drop-down on odd number of clicks
    else:
        return [{'display': 'block'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}]


@app.callback(Output('dropdown1', 'options'), [Input('url', 'href')])
def set_dropdown(href):
    if href is not None:
        # Get list of end dates from MongoDB
        rfm = RFMData()
        end_dates_iso = rfm.get_all_end_dates(dummy_obj)
        # print(end_dates_iso)

        # Parse the end dates iso to get month and year
        period_values = []
        for value in end_dates_iso:
            period_values.append(value.strftime("%b-%Y"))

        # Printing month-year format
        # print(period_values)

        # Set dropdown values
        dropdown_values = [dict(label=x, value=i) for i, x in enumerate(period_values)]
        # print(dropdown_values)
        return dropdown_values


# Set dropdown3 and dropdown4 based on segment_size of object_id
@app.callback([Output('dropdown3', 'options'), Output('dropdown4', 'options')], [Input('url', 'href')])
def set_fm_dropdown_values(href):
    if href is not None:

        rfm = RFMData()

        # Get RFM model size:
        segment_size = rfm.get_segment_size(dummy_obj)

        dropdown_labels = []
        for i in range(1, segment_size + 1):
            value = "value: " + str(i)
            dropdown_labels.append(value)

        dropdown_values = [dict(label=x, value=i + 1) for i, x in enumerate(dropdown_labels)]

        return dropdown_values, dropdown_values


@app.callback(Output('graph1', 'figure'),
              [Input('dropdown1', 'value'), Input('dropdown2', 'value'), Input('dropdown3', 'value'),
               Input('dropdown4', 'value'), Input('url', 'href')]
              )
def update_fig(dropdown1, dropdown2, dropdown3, dropdown4, href):
    if href is not None:
        # print(customer_df[0:10])

        # Set access token
        mapbox_access_token = 'pk.eyJ1IjoiYWhzLXZhIiwiYSI6ImNraGsyMWVmdDByOWszNnNkdzJqcHpwOWMifQ.llITOAaVvDUflVgenIPPlw'

        rfm = RFMData()

        # Should make a call in maps not here
        rfm_model = pd.DataFrame(rfm.get_records(dummy_obj))
        # print(rfm_model)
        # print(rfm_model.loc[0]['segment_d'])

        # Get customers data and append r, f, m, and rfm
        customer = Customer()

        # Get customer data
        customer_df = pd.DataFrame(customer.get_customer_data())

        # rfm

        # Initialize labels as 1
        customer_df["r"] = np.nan
        customer_df["f"] = np.nan
        customer_df["m"] = np.nan
        customer_df["rfm"] = np.nan

        # Randomly generating the score values
        # print(dropdown1)

        # Retrieve that particular row
        rfm_model = rfm_model.iloc[[dropdown1]]
        rfm_model.reset_index(inplace=True)
        # print(rfm_model)

        # print(rfm_model)
        # print(rfm_model.columns)

        # Update values based on the RFM segmentation

        # Get list of customers with different R scores and Update r label
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['R_score1']), 'r'] = 1
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['R_score2']), 'r'] = 2
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['R_score3']), 'r'] = 3
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['R_score4']), 'r'] = 4
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['R_score5']), 'r'] = 5

        # Get list of customers with different F,M scores and Update f,m label
        for i in range(rfm_model['segment_count'].item()):
            j = i + 1
            f_var_name = "F_score" + str(j)
            customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0][f_var_name]), 'f'] = j

            m_score_name = "M_score" + str(j)
            customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0][m_score_name]), 'm'] = j

        # print(rfm_model['segment_count'].item())

        # print(customer_df)

        # Get list of different segmented customers and Update rfm label column
        for i in range(rfm_model['segment_count'].item()):
            val = "segment_" + chr(65 + i)
            customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0][val]), 'rfm'] = chr(65 + i)

        print(customer_df)
        print(customer_df.columns)

        # Remove customers with no label
        customer_df = customer_df[customer_df['rfm'].notna()]
        customer_df = customer_df.sort_values(by=["rfm"])
        customer_df.reset_index(inplace=True)

        print(customer_df)
        print(customer_df.columns)

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

        locations = []
        for lbl in current_df['rfm'].unique():
            # Different classes
            new_df = current_df.loc[current_df["rfm"] == lbl]
            # print('Length of new df is:')
            # print(len(new_df))
            # print(lbl)
            current_trace_name = "Class-" + lbl + " " + str(len(new_df))

            locations.append(go.Scattermapbox(
                lon=new_df['long'],
                lat=new_df['lat'],
                name=current_trace_name,
                mode='markers',
                marker=dict(color=color_val[lbl], size=6),
                # marker=go.scattermapbox.Marker(
                #     size=6,
                #     color=new_df["rfm_color_values"]
                # ),
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
                # title=dict(text="RFM Segments", font=dict(size=50, color='green')),
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
        }
