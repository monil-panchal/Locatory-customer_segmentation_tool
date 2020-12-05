import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask_login import current_user

from app import app

"""
This is the main UI component for showing the user details 
"""
layout = dbc.Container([
    html.Br(),
    dbc.Container([
        dcc.Location(id='urlProfile', refresh=True),
        html.H3('Profile Management'),
        html.Hr(),
        dbc.Row([

            dbc.Col([
                dbc.Label('Username:'),
                html.Br(),
                html.Br(),
                dbc.Label('Email:'),
            ], md=2),

            dbc.Col([
                dbc.Label(id='username', className='text-success'),
                html.Br(),
                html.Br(),
                dbc.Label(id='email', className='text-success'),
            ], md=4)
        ]),
    ], className='jumbotron')
])

"""
This callback is used for showing the current user details 
"""
@app.callback(
    [Output('username', 'children'),
     Output('email', 'children')],
    [Input('page-content', 'children')])
def display_current_user_details(page_content):
    return current_user.get_id(), current_user.get_id()
