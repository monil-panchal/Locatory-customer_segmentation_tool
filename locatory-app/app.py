import os

import dash
from flask_login import LoginManager, UserMixin

from apps.user.user import AppUser
from dash import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import os
import pandas as pd
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

mapbox_access_token = 'pk.eyJ1IjoiYWhzLXZhIiwiYSI6ImNraGsyMWVmdDByOWszNnNkdzJqcHpwOWMifQ.llITOAaVvDUflVgenIPPlw'


app = dash.Dash(__name__, suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server
server.config.update(
    SECRET_KEY=os.urandom(12)
)

# LoginManager
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'


# Creating User class with UserMixin
class User(UserMixin):
    def __init__(self, user_json):
        self.user_json = user_json

    def get_id(self):
        object_id = self.user_json.get('email')
        return str(object_id)


# callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    user_json = AppUser().get_customer_data(user_id)
    return User(user_json)



