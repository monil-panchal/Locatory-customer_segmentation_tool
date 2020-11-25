import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from apps.user.customer import Customer
from apps.rfm.rfm import RFMData
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
from app import app
import random

# dbc.Container([
#
# # html.H2('Default RFM dashboard'),
# html.Hr(),

layout = html.Div([

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
                        dcc.Dropdown(id="dropdown3", value=0,
                                     options=[{"label": "value: 1", "value": 1},
                                              {"label": "value: 2", "value": 2},
                                              {"label": "value: 3", "value": 3},
                                              {"label": "value: 4", "value": 4},
                                              {"label": "value: 5", "value": 5}], multi=True
                                     # , style={'color': 'blue', 'backgroundColor': 'blue'}
                                     ),
                        ],
                       style={'height': '100%', 'width': '120%', 'display': 'none'}, id="dropdown3_component"
                       ),
            # ),

            html.Label(["Select M value",
                        dcc.Dropdown(id="dropdown4", value=0,
                                     options=[{"label": "value: 1", "value": 1},
                                              {"label": "value: 2", "value": 2},
                                              {"label": "value: 3", "value": 3},
                                              {"label": "value: 4", "value": 4},
                                              {"label": "value: 5", "value": 5}], multi=True
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
            'left': '120px',
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
        'left': '120px',
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


@app.callback(
    Output(component_id='slider-container', component_property='style'),
    [Input(component_id='dropdown', component_property='value')])
@app.callback(Output('dropdown1', 'options'), [Input('url', 'href')])
def set_dropdown(href):
    if href is not None:
        # Get list of end dates from MongoDB
        rfm = RFMData()
        end_dates_iso = rfm.get_all_end_dates()
        # print(end_dates_iso)

        # Parse the end dates iso to get month and year
        period_values = []
        for value in end_dates_iso:
            period_values.append(value.strftime("%b-%Y"))

        # Printing month-year format
        # print(period_values)

        # Set dropdown calues
        dropdown_values = [dict(label=x, value=i) for i, x in enumerate(period_values)]
        print(dropdown_values)
        return dropdown_values


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
        rfm_model = pd.DataFrame(rfm.get_records())
        # print(rfm_model)
        # print(rfm_model.loc[0]['segment_d'])

        # Get customers data and append r, f, m, and rfm
        customer = Customer()

        # Get customer data
        customer_df = pd.DataFrame(customer.get_customer_data())

        # rfm
        segment_d_customer_id = rfm_model.loc[0]['segment_d']

        # Initialize labels as 1
        customer_df["r"] = 1
        customer_df["f"] = 1
        customer_df["m"] = 1
        customer_df["rfm"] = 1

        # Randomly generating the score values TODO: Remove this and integrate with the actual RFM Model.
        #  TODO:  Remove these below lines of code from 202 and flow is maintained from line 227 without any code
        #   addition.
        # print(dropdown1)

        # Retrieve that particular row
        rfm_model = rfm_model.iloc[[dropdown1]]
        rfm_model.reset_index(inplace=True)
        # print(rfm_model)
        rfm_model.at[0, 'R_score1'] = customer_df[0:18973]["customer_id"].to_list()
        rfm_model.at[0, 'R_score2'] = customer_df[18973:37946]["customer_id"].to_list()
        rfm_model.at[0, 'R_score3'] = customer_df[37946:56919]["customer_id"].to_list()
        rfm_model.at[0, 'R_score4'] = customer_df[56919:75894]["customer_id"].to_list()
        rfm_model.at[0, 'R_score5'] = customer_df[75894:94866]["customer_id"].to_list()

        rfm_model.at[0, 'F_score1'] = customer_df[0:18973]["customer_id"].to_list()
        rfm_model.at[0, 'F_score2'] = customer_df[18973:37946]["customer_id"].to_list()
        rfm_model.at[0, 'F_score3'] = customer_df[37946:56919]["customer_id"].to_list()
        rfm_model.at[0, 'F_score4'] = customer_df[56919:75894]["customer_id"].to_list()
        rfm_model.at[0, 'F_score5'] = customer_df[75894:94866]["customer_id"].to_list()

        rfm_model.at[0, 'M_score1'] = customer_df[0:18973]["customer_id"].to_list()
        rfm_model.at[0, 'M_score2'] = customer_df[18973:37946]["customer_id"].to_list()
        rfm_model.at[0, 'M_score3'] = customer_df[37946:56919]["customer_id"].to_list()
        rfm_model.at[0, 'M_score4'] = customer_df[56919:75894]["customer_id"].to_list()
        rfm_model.at[0, 'M_score5'] = customer_df[75894:94866]["customer_id"].to_list()

        rfm_model.at[0, 'segment_a'] = customer_df[0:18973]["customer_id"].to_list()
        rfm_model.at[0, 'segment_b'] = customer_df[18973:37946]["customer_id"].to_list()
        rfm_model.at[0, 'segment_c'] = customer_df[37946:56919]["customer_id"].to_list()
        rfm_model.at[0, 'segment_d'] = customer_df[56919:75894]["customer_id"].to_list()
        rfm_model.at[0, 'segment_e'] = customer_df[75894:94866]["customer_id"].to_list()

        # print(rfm_model)
        # print(rfm_model.columns)

        # Update values based on the RFM segmentation

        # Get list of customers with different R scores and Update r label
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['R_score1']), 'r'] = 1
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['R_score2']), 'r'] = 2
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['R_score3']), 'r'] = 3
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['R_score4']), 'r'] = 4
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['R_score5']), 'r'] = 5

        # Get list of customers with different F scores and Update f label
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['F_score1']), 'f'] = 1
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['F_score2']), 'f'] = 2
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['F_score3']), 'f'] = 3
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['F_score4']), 'f'] = 4
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['F_score5']), 'f'] = 5

        # Get list of customers with different M scores and Update m label
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['M_score1']), 'm'] = 1
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['M_score2']), 'm'] = 2
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['M_score3']), 'm'] = 3
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['M_score4']), 'm'] = 4
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['M_score5']), 'm'] = 5

        # Get list of different segmented customers and Update rfm label column
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['segment_a']), 'rfm'] = 'a'
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['segment_b']), 'rfm'] = 'b'
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['segment_c']), 'rfm'] = 'c'
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['segment_d']), 'rfm'] = 'd'
        customer_df.loc[customer_df["customer_id"].isin(rfm_model.loc[0]['segment_e']), 'rfm'] = 'e'

        print(customer_df)
        print(customer_df.columns)

        # Define a list of colors
        # Index0 - Empty, Green - class A , Red - class B, Blue - class C, Orange - class D, Yellow - class E
        color_val = {'a': 'green',
                     'b': 'red',
                     'c': 'blue',
                     'd': 'orange',
                     'e': 'yellow'}
        # color_list = ["", "green", "red", "blue", "orange", "yellow"]
        # final_color_values = []
        # for item in customer_df["rfm"].tolist():
        #     final_color_values.append(color_list[item])
        #
        # customer_df["rfm_color_values"] = final_color_values

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
            print('Length of new df is:')
            print(len(new_df))
            current_trace_name = "Class-" + lbl

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
                        size=12, ),
                ),
                # annotations=[
                #     dict(
                #         x=0,
                #         y=0.75,
                #         xref='paper',
                #         yref='paper',
                #         text='Segments',
                #         showarrow=False
                #     )
                # ]
            )
        }
