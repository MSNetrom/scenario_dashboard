import pandas as pd
import dash_bootstrap_components as dbc
import dash
from layout.global_layout import content, sidebar
from dash import dcc, html
from callbacks.callbacks import get_callbacks
import os
from dash import Dash


# os.environ['XDG_RUNTIME_DIR'] = '/tmp/runtime-danare'
# https://stackoverflow.com/questions/69570145/how-to-change-the-website-tab-name-in-dash-plotly-using-python


app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "Dashboard"
app.layout = html.Div([dcc.Location(id="url"), sidebar, content],)

# get callbacks
get_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)
