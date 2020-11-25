import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

class CustomSegmentationParamsModal:

    @staticmethod
    def get_select_country_div():
        return html.Div([
            dbc.Label("Select Country"),
            dcc.Checklist(
                id="country_checkbox_modal",
                options=[

                ],
                value=['Brazil'],
                labelStyle={'display': 'inline-block'}
            ),
        ])

    @staticmethod
    def get_select_state_div():
        return html.Div([
            dbc.Label("Select State"),
            dcc.Dropdown(
                id="state_dropdown_modal",
                options=[

                ],
                value=[],
                multi=True,
            ),
        ])

    @staticmethod
    def get_select_city_div():
        return html.Div([
            dbc.Label("Select City"),
            dcc.Dropdown(
                id="city_dropdown_modal",
                options=[
                ],
                value=[],
                multi=True,
            ),
        ])

    @staticmethod
    def get_select_segmentation_algorithm_div():
        return html.Div([
            dbc.Label("Select Segmentation Algorithm"),
            dcc.Dropdown(
                id="segmentation_algorithm_modal",
                options=[{'label': 'Recency-Frequency-Monetory (RFM)', 'value': 'RFM'}],
                value=['RFM'],
            ),
        ])

    @staticmethod
    def get_select_gender_div():
        return html.Div([
            dbc.Label("Select Gender"),
            dcc.Checklist(
                id="gender_checkbox_modal",
                options=[

                ],
                value=['Male'],
                labelStyle={'display': 'inline-block'}
            ),
        ])

    @staticmethod
    def get_select_age_range_div():
        return html.Div([
            html.H6('Select Age Range (in years)'),
            dcc.RangeSlider(
                id='age-range-slider_modal',
                step=1,
            ),
            html.Div(id='output-container-range-slider-age_modal', style={'textAlign': 'center'})
        ])

    @staticmethod
    def get_select_income_range_div():
        return html.Div([
            html.H6('Select Income Range'),
            dcc.RangeSlider(
                id='income-range-slider_modal',
                step=100,
            ),
            html.Div(id='output-container-range-slider-income_modal', style={'textAlign': 'center'})
        ])

    @staticmethod
    def get_modal_component_ids():
        # ids of components defined in the get_modal_elements()
        modal_component_ids = ["custom_params_title", "input_segments", "input_data", "segment-segregator_modal", "gender_checkbox_modal",
                               "age-range-slider_modal", "income-range-slider_modal", "country_checkbox_modal",
                               "state_dropdown_modal", "city_dropdown_modal", "segmentation_algorithm_modal"]
        return modal_component_ids

    @staticmethod
    def get_modal_elements():
        return [
            dbc.ModalHeader("Create segmentation params"),
            dbc.ModalBody([
                html.Div([
                    dbc.Toast(
                        "",
                        id="toast-message",
                        header="",
                        icon="primary",
                        duration=3000,
                    ),
                ]),
                html.Div(
                    [
                        dbc.Input(id="custom_params_title", placeholder="Enter title of custom params", type="text", maxLength=200),
                        html.Br(),
                    ]
                ),
                html.Div(
                    [
                        dbc.Input(id="input_segments", placeholder="Enter no of segments", type="number", min=3,
                                  max=10),
                        html.Br(),
                    ]
                ),
                html.Div(
                    [
                        dbc.Input(id="input_data", placeholder="Enter data period (in months)", type="number", min=1,
                                  max=24),
                        html.Br(),
                    ]
                ),
                html.Div([
                    html.H6('Select Segments Range'),
                    dcc.RangeSlider(
                        id='segment-segregator_modal',
                        min=0,
                        max=100,
                        value=[],
                        pushable=1
                    ),
                    html.Div(id='output-container-segment-segregator_modal', style={'textAlign': 'center'})
                ]
                ),
                # demography
                CustomSegmentationParamsModal.get_select_gender_div(),
                CustomSegmentationParamsModal.get_select_age_range_div(),
                CustomSegmentationParamsModal.get_select_income_range_div(),

                # geography
                CustomSegmentationParamsModal.get_select_country_div(),
                CustomSegmentationParamsModal.get_select_state_div(),
                CustomSegmentationParamsModal.get_select_city_div(),

                CustomSegmentationParamsModal.get_select_segmentation_algorithm_div()

            ]),
            dbc.ModalFooter(
                dbc.Row([
                    dbc.Button("Create", id="create", color="success", className="mr-1"),
                    dbc.Button("Close", id="close", color="primary", className="mr-1"),
                ]),
            ),
        ]