import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask_login import login_user

from app import app, User
from apps.user.user import AppUser

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
                    className='form-control'
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
                    n_clicks=0,
                    type='submit',
                    id='loginButton',
                    className='btn btn-primary btn-lg'
                ),
                html.Br(),
            ], className='center', style={'width': '51%'}),
            dbc.Container(
                html.Div(id='error'
                         ),
            ),
        ]),
    ], className='jumbotron')
])


@app.callback([Output('urlLogin', 'pathname'),
               Output('error', 'children')],
              [Input('loginButton', 'n_clicks'),
               Input('usernameBox', 'n_submit'),
               Input('passwordBox', 'n_submit')],
              [State('usernameBox', 'value'),
               State('passwordBox', 'value')]
              )
def success(n_clicks, usernameSubmit, passwordSubmit, username, password):
    print('calling the callback')
    print(f'username: {username}')
    print(f'password: {password}')
    if None not in (username, password):
        user = AppUser().get_customer_data(username=username)
        print(f'user from db: {user}')
        if user:
            if password == user['password']:
                print('user authenticated successfully')
                loggedin_user = User(user)
                login_user(loggedin_user)
                return '/sales_dashboard', None
            else:
                print('user not authenticated successfully')
                return '/', 'Please check your credentials'
        else:
            return '/', 'Please check your credentials'
    else:
        return '/', None
