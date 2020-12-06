import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask_login import login_user
from werkzeug.security import check_password_hash

from app import app, User
from apps.db.dao.user_dao import AppUser

"""
This is the main UI component for user login page
"""
layout = dbc.Container([
    html.Br(),
    dbc.Container([
        dcc.Location(id='urlLogin', refresh=True),
        html.Div([
            dbc.Container(
                html.Img(
                    src='/assets/locatory-logo-removebg-preview.png',
                    className='center'
                ),
            ),
            html.Br(),
            dbc.Container(id='loginType', children=[
                dcc.Input(
                    placeholder='Enter your username',
                    type='text',
                    id='usernameBox',
                    className='form-control',
                ),
                html.Br(),
                dcc.Input(
                    placeholder='Enter your password',
                    type='password',
                    id='passwordBox',
                    className='form-control'
                ),
                html.Br(),
                html.Button(
                    children='Login',
                    n_clicks=-1,
                    type='submit',
                    id='loginButton',
                    className='btn btn-primary btn-lg'
                ),
                html.Br(),
            ], className='center', style={'width': '51%'}),
            dbc.Toast(
                "Username or password is incorrect or empty",
                id="error-toast",
                header="Error while signing you in",
                is_open=False,
                dismissable=True,
                icon="danger",
                duration=5000,
                style={"position": "fixed", "top": '5%', "left": '35%', "width": '25%'},
            ),
        ]),
    ], className='jumbotron')
])

"""
This callback is used for user authentication and login
"""
@app.callback([Output('urlLogin', 'pathname'),
               Output("error-toast", "is_open")],
              [Input('loginButton', 'n_clicks')],
              [State('usernameBox', 'value'),
               State('passwordBox', 'value')])
def user_authentication(n_clicks, username, password):
    if n_clicks < 0:
        return '/', None

    if None not in (username, password):
        user = AppUser().get_customer_data(username=username)
        if user:
            if check_password_hash(user['password'], password):
                print('dao authenticated successfully')
                loggedin_user = User(user)
                login_user(loggedin_user)
                return '/sales_dashboard', False
            else:
                print('dao not authenticated successfully')
                return '/', True
        else:
            return '/', True
    else:
        return '/', True
