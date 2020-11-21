# import dash_bootstrap_components as dbc
# import dash_core_components as dcc
# import dash_html_components as html
# import pandas as pd
# from apps.user.customer import Customer
# from dash.dependencies import Output, Input, State
# import plotly.graph_objects as go
# from app import app
# import random
#
# mapbox_access_token = 'pk.eyJ1IjoiYWhzLXZhIiwiYSI6ImNraGsyMWVmdDByOWszNnNkdzJqcHpwOWMifQ.llITOAaVvDUflVgenIPPlw'
#
# # print(mapbox_access_token[0:10])
# customer = Customer()
#
# # Get labels of each customer
# random.seed(4)
# labels = [random.randint(1, 5) for _ in range(0, 94866)]
# # print(labels)
#
# # Get customer data
# customer_df = pd.DataFrame(customer.get_customer_data())
#
# # Assign labels retrieved
# customer_df["rfm"] = labels
#
# # RFM values
# customer_df["r"] = labels
# customer_df["f"] = labels
# customer_df["m"] = labels
#
# # Define a list of colors
# # Index0 - Empty, Green - class A , Red - class B, Blue - class C, Orange - class D, Yellow - class E
# color_list = ["", "green", "red", "blue", "orange", "yellow"]
# final_color_values = []
# for item in customer_df["rfm"].tolist():
#     final_color_values.append(color_list[item])
#
# customer_df["rfm_color_values"] = final_color_values
#
# # print(customer_df)
# # print(customer_df.columns)
#
# layout = dbc.Container([
#
#     html.H2('Default RFM dashboard'),
#     html.Hr(),
#
#     html.Div([
#
#         # Borough_checklist
#         dbc.FormGroup([
#             dbc.Row([
#                 dbc.Col(
#                     # dbc.Label("Choose Dataset"),
#                     html.Label(["Select Dataset",
#                                 dcc.Dropdown(id="dropdown1", value=1),
#                                 ],
#                                style={'width': '50%'}),
#                 ),
#                 dbc.Col(
#                     html.Label(["Select R value",
#                                 dcc.Dropdown(id="dropdown2", value=0,
#                                              options=[{"label": "value: 1", "value": 1},
#                                                       {"label": "value: 2", "value": 2},
#                                                       {"label": "value: 3", "value": 3},
#                                                       {"label": "value: 4", "value": 4},
#                                                       {"label": "value: 5", "value": 5}], multi=True),
#                                 ],
#                                style={'width': '50%'}),
#                 ),
#                 dbc.Col(
#                     html.Label(["Select F value",
#                                 dcc.Dropdown(id="dropdown3", value=0,
#                                              options=[{"label": "value: 1", "value": 1},
#                                                       {"label": "value: 2", "value": 2},
#                                                       {"label": "value: 3", "value": 3},
#                                                       {"label": "value: 4", "value": 4},
#                                                       {"label": "value: 5", "value": 5}], multi=True),
#                                 ],
#                                style={'width': '50%'}),
#                 ),
#                 dbc.Col(
#                     html.Label(["Select M value",
#                                 dcc.Dropdown(id="dropdown4", value=0,
#                                              options=[{"label": "value: 1", "value": 1},
#                                                       {"label": "value: 2", "value": 2},
#                                                       {"label": "value: 3", "value": 3},
#                                                       {"label": "value: 4", "value": 4},
#                                                       {"label": "value: 5", "value": 5}], multi=True),
#                                 ],
#                                style={'width': '50%'}),
#                 ),
#             ]),
#         ]),
#     ]),
#
#     html.Div([
#         dbc.Row([
#             dbc.Col(dcc.Graph(id='graph1', config={'displayModeBar': False, 'scrollZoom': True},
#                               style={'padding-bottom': '2px', 'height': '100vh'})),
#         ]),
#     ]),
# ], className="mt-4")
#
#
# @app.callback(Output('graph1', 'figure'),
#               [Input('dropdown1', 'value'), Input('dropdown2', 'value'), Input('dropdown3', 'value'),
#                Input('dropdown4', 'value')]
#               )
# def update_fig(dropdown1, dropdown2, dropdown3, dropdown4):
#     # print(customer_df[0:10])
#
#     if dropdown2 == 0 or dropdown2 is None or not dropdown2:
#         current_df = customer_df
#     else:
#         # Condensing dataframe based on R value
#         current_df = customer_df.loc[customer_df["r"].isin(dropdown2)]
#
#     if dropdown3 == 0 or dropdown3 is None or not dropdown3:
#         current_df = current_df
#     else:
#         # Condensing dataframe based on F value
#         current_df = current_df.loc[current_df["f"].isin(dropdown3)]
#
#     if dropdown4 == 0 or dropdown4 is None or not dropdown4:
#         current_df = current_df
#     else:
#         # Condensing dataframe based on M value
#         current_df = current_df.loc[current_df["m"].isin(dropdown4)]
#
#     locations = [go.Scattermapbox(
#         lon=current_df['long'],
#         lat=current_df['lat'],
#         mode='markers',
#         marker=go.scattermapbox.Marker(
#             size=6,
#             color=current_df["rfm_color_values"]
#         ),
#     )]
#     return {
#         'data': locations,
#         'layout': go.Layout(
#             uirevision='foo',
#             clickmode='event+select',
#             hovermode='closest',
#             hoverdistance=2,
#             title=dict(text="RFM Segments", font=dict(size=50, color='green')),
#             mapbox=dict(
#                 accesstoken=mapbox_access_token,
#                 bearing=0,
#                 style='light',
#                 center=dict(
#                     lat=-22.80105,
#                     lon=-45.945155
#                 ),
#                 pitch=0,
#                 zoom=3
#             ),
#         )
#     }
