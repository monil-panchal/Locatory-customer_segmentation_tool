import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask_login import current_user, logout_user

from app import app
from apps.views import login, map_dashboard, other_dashboard, profile, custom_maps

navBar = dbc.Navbar(id='navBar',
                    children=[],
                    sticky='top',
                    color='primary',
                    className='navbar navbar-expand-lg navbar-dark bg-primary',
                    )

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        navBar,
        html.Div(id='page-content')
    ])
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        if current_user.is_authenticated:
            return map_dashboard.layout
        else:
            return login.layout

    if pathname == '/map_dashboard':
        if current_user.is_authenticated:
            return map_dashboard.layout
        else:
            return login.layout

    if pathname == '/other_dashboard':
        if current_user.is_authenticated:
            return other_dashboard.layout
        else:
            return login.layout

    if pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            return login.layout
        else:
            return login.layout

    if pathname == '/profile':
        if current_user.is_authenticated:
            return profile.layout
        else:
            return login.layout

    if pathname == '/custom_maps_list':
        if current_user.is_authenticated:
            return custom_maps.layout
        else:
            return login.layout


@app.callback(
    Output('navBar', 'children'),
    [Input('page-content', 'children')])
def navBar(input1):
    if current_user.is_authenticated:
        navBarContents = [
            dbc.NavItem(dbc.NavLink('Map Dashboard', href='/map_dashboard')),
            dbc.NavItem(dbc.NavLink('Default RFM Dashboard', href='/other_dashboard')),
            dbc.NavItem(dbc.NavLink('Custom Maps List', href='/custom_maps_list')),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label=current_user.get_id(),
                children=[
                    dbc.DropdownMenuItem('Profile', href='/profile'),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem('Logout', href='/logout'),
                ],
            ),
        ]
        return navBarContents
    else:
        return ''


if __name__ == '__main__':
    app.run_server(debug=True)
