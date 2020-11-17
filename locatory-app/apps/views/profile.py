import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from app import app, User
from flask_login import current_user

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

@app.callback(
    Output('username', 'children'),
    [Input('page-content', 'children')])
def currentUserName(pageContent):
    print(f'current_user: {current_user}')
    print(f'current_user.get_id(): {current_user.get_id()}')
    return current_user.get_id()


@app.callback(
    Output('email', 'children'),
    [Input('page-content', 'children')])
def currentUserEmail(pageContent):
    return current_user.get_id()
