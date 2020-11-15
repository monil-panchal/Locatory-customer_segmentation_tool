from dash import dash
import dash_bootstrap_components as dbc
import dash_html_components as html

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1('Welcome to Locatory app')
])

if __name__ == '__main__':
    app.run_server(debug=True)
