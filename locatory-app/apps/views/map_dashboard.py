import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from apps.user.customer import Customer
from dash.dependencies import Input, Output, State
from app import app

layout = html.Div([

        html.H2('Map Dashboard data'),
        html.Hr(),


], className="mt-4")

# brazil_state_code_map = {
# 'AC':'Acre',
# 'AL':'Alagoas',
# 'AP':'Amapá',
# 'AM':'Amazonas',
# 'BA':'Bahia',
# 'CE':'Ceará',
# 'DF':'Distrito Federal',
# 'ES':'Espírito Santo',
# 'GO':'Goiás',
# 'MA':'Maranhão',
# 'MT':'Mato Grosso',
# 'MS':'Mato Grosso do Sul',
# 'MG':'Minas Gerais',
# 'PA':'Pará',
# 'PB':'Paraíba',
# 'PR':'Paraná',
# 'PE':'Pernambuco',
# 'PI':'Piauí',
# 'RJ':'Rio de Janeiro',
# 'RN':'Rio Grande do Norte',
# 'RS':'Rio Grande do Sul',
# 'RO':'Rondônia',
# 'RR':'Roraima',
# 'SC':'Santa Catarina',
# 'SP':'São Paulo',
# 'SE':'Sergipe',
# 'TO':'Tocantins',
# }
# mapbox_access_token = 'pk.eyJ1IjoiYWhzLXZhIiwiYSI6ImNraGsyMWVmdDByOWszNnNkdzJqcHpwOWMifQ.llITOAaVvDUflVgenIPPlw'
# customer = Customer()
# customer_df = pd.DataFrame(customer.get_customer_data())
#
# layout = dbc.Container([
#
#         html.H2('Map Dashboard'),
#         html.Hr(),
#         html.Div([
#                 dbc.Label("Select Country"),
#                 dcc.Checklist(
#                     id="country_checkbox",
#                     options=[
#                         {'label': key, 'value': key} for key in sorted(customer_df['customer_country'].unique())
#                     ],
#                     value=['Brazil'],
#                     labelStyle={'display': 'inline-block'}
#                 ) ,
#         ]),
#         html.Div([
#                 dbc.Label("Select State"),
#                 dcc.Checklist(
#                     id="state_checkbox",
#                     options=[
#                         {'label': f"{brazil_state_code_map[key]}", 'value': key} for key in sorted(customer_df['customer_state'].unique())
#                     ],
#                     value=list(brazil_state_code_map.keys())[:7],
#                     labelStyle={'display': 'inline-block'}
#                 ),
#         ]),
#         # html.Br(),
#         # html.Div([
#         #         dbc.Label("Select City"),
#         #         dcc.Checklist(
#         #             id="city_checkbox",
#         #             options=[
#         #             ],
#         #             value=[],
#         #             labelStyle={'display': 'inline-block'}
#         #         ) ,
#         # ]),
#         html.Br(),
#         html.Div([
#                 dbc.Label("Select Gender"),
#                 dcc.Checklist(
#                     id="gender_checkbox",
#                     options=[
#                         {'label': key, 'value': key} for key in sorted(customer_df['gender'].unique())
#                     ],
#                     value=['Male'],
#                     labelStyle={'display': 'inline-block'}
#                 ) ,
#         ]),
#         html.Br(),
#         html.Div([
#                 html.H6('Select Age Range (in years)'),
#             dcc.RangeSlider(
#                 id='age-range-slider',
#                 min=customer_df['age'].min(),
#                 max=customer_df['age'].max(),
#                 value=[customer_df['age'].min(), customer_df['age'].min()+3],
#                 step=1,
#                 marks={int(key):{'label': f"{key}"} for key in range(0, customer_df['age'].max()+1, 5)},
#
#             ),
#             html.Div(id='output-container-range-slider-age', style={'textAlign': 'center'})
#         ]),
#         html.Br(),
#         html.Div([
#                 html.H6('Select Income Range'),
#             dcc.RangeSlider(
#                 id='income-range-slider',
#                 min=customer_df['income'].min(),
#                 max=customer_df['income'].max(),
#                 value=[customer_df['income'].min(), customer_df['income'].min()+5000],
#                 step=100,
#                 marks={int(key):{'label': f"{key}"} for key in range(0, customer_df['income'].max()+1, 5000)},
#
#             ),
#             html.Div(id='output-container-range-slider-income', style={'textAlign': 'center'})
#         ]),
#         # map
#         html.Div([
#                 dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True},
#                           style={'padding-bottom': '2px', 'height': '100vh'})
#         ])
#
# ], className="mt-4")
#
#
# @app.callback(Output('graph', 'figure'), [Input('gender_checkbox', 'value'), Input('age-range-slider', 'value'), Input('income-range-slider', 'value'), Input('country_checkbox', 'value'), Input('state_checkbox', 'value')])
# def update_fig(gender_values, age_range, income_range, countries, states):
#     print(age_range,gender_values, income_range,countries, states)
#     print(customer_df[0:3])
#     df = customer_df
#     if countries is not None:
#         df = df.loc[df['customer_country'].isin(countries)]
#     if states is not None:
#         df = df.loc[df['customer_state'].isin(states)]
#     if gender_values is not None:
#         df = df.loc[df['gender'].isin(gender_values)]
#         print(len(df), len(df['gender'].isin(gender_values)))
#     if age_range is not None and len(age_range)==2:
#         df = df.loc[(df['age']>=age_range[0]) & (df['age']<=age_range[1])]
#     if income_range is not None and len(income_range)==2:
#         df = df.loc[(df['income']>=income_range[0]) & (df['income']<=income_range[1])]
#
#     locations = [go.Scattermapbox(
#         lon=df['long'],
#         lat=df['lat'],
#         mode='markers',
#         marker=go.scattermapbox.Marker(
#             size=6
#         ),
#     )]
#     return {
#         'data': locations,
#         'layout': go.Layout(
#             uirevision='foo',
#             clickmode='event+select',
#             hovermode='closest',
#             hoverdistance=2,
#             title=dict(text="MapBox", font=dict(size=50, color='green')),
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
#
#
# @app.callback(
#     Output('output-container-range-slider-age', 'children'),
#     [Input('age-range-slider', 'value')])
# def update_age_range_div(value):
#     return 'Selected Age Range "{}"'.format(value)
#
# @app.callback(
#     Output('output-container-range-slider-income', 'children'),
#     [Input('income-range-slider', 'value')])
# def update_income_range_div(value):
#     return 'Selected Income Range: "{}"'.format(value)
#
# @app.callback(
#         Output('state_checkbox', 'options'),
#         [Input('country_checkbox', 'value')],
#         )
# def update_state_checkbox(value):
#     print(f"options",value)
#     df = customer_df.loc[customer_df['customer_country'].isin(value)]
#     return [
#         {'label': f"{brazil_state_code_map[key]}", 'value': key} for key in
#         sorted(df['customer_state'].unique())
#     ]
