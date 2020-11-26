import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash import callback_context
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from apps.user.customer import Customer
from apps.user.custom_segmentation_params import SegmentationParameters
from apps.views.custom_segmentation_params_modal import CustomSegmentationParamsModal
from dash.dependencies import Input, Output, State
from app import app
from apps.config.constants import brazil_state_code_map, mapbox_access_token
from apps.user.RFM import RFM

@app.callback(
    Output('output-container-range-slider-age_modal', 'children'),
    [Input('age-range-slider_modal', 'value')])
def update_age_range_div_modal(value):
    return 'Selected Age Range "{}"'.format(value)

@app.callback(
    Output('output-container-range-slider-income_modal', 'children'),
    [Input('income-range-slider_modal', 'value')])
def update_income_range_div_modal(value):
    return 'Selected Income Range: "{}"'.format(value)

@app.callback(
    Output('segment-segregator_modal', 'value'), Output('segment-segregator_modal', 'pushable'),
    [Input('input_segments', 'value')])
def update_segment_seperator_modal(value):
    if value is None or value<3 or value>10:
        return [], 0
    else:
        return list(np.arange(0, 100, 100/int(value))), 5

@app.callback(
    Output('output-container-segment-segregator_modal', 'children'),
    [Input('segment-segregator_modal', 'value')])
def update_segment_seperator_text_modal(value):
    if len(value)>0 and len(value)<25:
        classes = []
        for i in range(0, len(value)):
            classes.append(chr(ord('A') + i))
        classes.reverse()
        class_range_text = []
        class_range_text.append(f"Class {classes[0]}: [{0} - {int(value[1])}]")
        for ind in range(1, len(value) - 1):
            class_range_text.append(f"Class {classes[ind]}: [{int(value[ind])} - {int(value[ind + 1])}]")
        class_range_text.append(f"Class {classes[-1]}: [{int(value[-1])} - {100}]")
        return "      ,        ".join(class_range_text)
    return ""

layout = dbc.Container([
            html.H2('Custom Maps List'),
            html.Hr(),
            dbc.Button("New custom segmentation params", id="open", color="success"),
            html.Br(),
            dbc.Modal(
                CustomSegmentationParamsModal.get_modal_elements(),
                id="modal",
                size="xl",
            ),
            html.Br(),
            dbc.Col(html.Div(id='cards-content'),),
        ], className="mt-4")

@app.callback(
            Output("toast-message", "header"), Output("toast-message", "children"),
            Output("toast-message", "is_open"), Output('country_checkbox_modal', 'options'),
            Output('gender_checkbox_modal', 'options'), Output('age-range-slider_modal', 'min'),
            Output('age-range-slider_modal', 'max'), Output('age-range-slider_modal', 'value'),
            Output('age-range-slider_modal', 'marks'), Output('income-range-slider_modal', 'min'),
            Output('income-range-slider_modal', 'max'), Output('income-range-slider_modal', 'value'),
            Output('income-range-slider_modal', 'marks'),
    [Input("open", "n_clicks"), Input("create", "n_clicks")],
    [State("modal", "is_open")] + [State(ele_id, "value") for ele_id in CustomSegmentationParamsModal.get_modal_component_ids()],
)
def toggle_modal(n1, create_button, is_open, *modal_component_states_args):
    print('toggle_modal', n1, create_button, is_open, modal_component_states_args)

    toast_message_header = ''
    toast_message_content = ''
    toast_message_open = False

    country_checkbox_options, \
    gender_checkbox_options, \
    age_range_slider_min, \
    age_range_slider_max, \
    age_range_slider_value, \
    age_range_slider_marks, \
    income_range_slider_min, \
    income_range_slider_max, \
    income_range_slider_value, \
    income_range_slider_marks = get_modal_filters()

    if is_open is True and create_button is not None:
        csp = SegmentationParameters()
        custom_params_dict = {}
        for key,val in zip(CustomSegmentationParamsModal.get_modal_component_ids(), modal_component_states_args):
            if key == 'segment-segregator_modal' and len(val)>0:
                val[0]=0
                custom_params_dict[key] = list(np.array(val) / 100)
                continue
            custom_params_dict[key] = val

        if custom_params_dict.get('input_data') is None or custom_params_dict.get('input_data')<1 \
                or custom_params_dict.get('input_data')>24:
            toast_message_header = "Validation Error"
            toast_message_content = "Data period must be between 1 and 24"
        if custom_params_dict.get('input_segments') is None \
                or custom_params_dict.get('input_segments')<3 or custom_params_dict.get('input_segments')>10:
            toast_message_header = "Validation Error"
            toast_message_content = "No of segments must be between 3 and 10"
        if custom_params_dict.get('custom_params_title') is None or custom_params_dict.get('custom_params_title').strip() == '' or len(custom_params_dict.get('custom_params_title')) > 200:
            toast_message_header = "Validation Error"
            toast_message_content = "Title can not be empty or more than 200 char long."
        elif csp.is_attribute_exist('title', custom_params_dict.get('custom_params_title')) is True:
            toast_message_header = "Validation Error"
            toast_message_content = f"Title '{custom_params_dict.get('custom_params_title')}' already exist."

        if toast_message_header != '':
            print(toast_message_content)
            toast_message_open = True
            return toast_message_header, toast_message_content, toast_message_open, \
                   country_checkbox_options, \
                   gender_checkbox_options, \
                   age_range_slider_min, \
                   age_range_slider_max, \
                   age_range_slider_value, \
                   age_range_slider_marks, \
                   income_range_slider_min, \
                   income_range_slider_max, \
                   income_range_slider_value, \
                   income_range_slider_marks
        try:
            inserted_id = csp.insert_custom_mapping(custom_params_dict)
            if inserted_id is not None and inserted_id is not False:
                response = RFM().create_rfm_segmentation(inserted_id)
                toast_message_header = "Success"
                if response is True:
                    toast_message_content = "Custom params and RFM segmentation successfully created"
                else:
                    toast_message_content = "Custom params successfully created, but RFM segmentation was failed."
            toast_message_open = True
        except Exception as e:
            print(e)

    return toast_message_header, toast_message_content, toast_message_open, country_checkbox_options, \
           gender_checkbox_options, \
           age_range_slider_min, \
           age_range_slider_max, \
           age_range_slider_value, \
           age_range_slider_marks, \
           income_range_slider_min, \
           income_range_slider_max, \
           income_range_slider_value, \
           income_range_slider_marks

def get_modal_filters():
    customer = Customer()
    customer_df = pd.DataFrame(customer.get_customer_data())
    country_checkbox_options = [{'label': key, 'value': key} for key in
                                sorted(customer_df['customer_country'].unique())]
    gender_checkbox_options = [{'label': key, 'value': key} for key in sorted(customer_df['gender'].unique())]
    age_range_slider_min = customer_df['age'].min()
    age_range_slider_max = customer_df['age'].max()
    age_range_slider_value = [customer_df['age'].min(), customer_df['age'].min() + 3]
    age_range_slider_marks = {int(key): {'label': f"{key}"} for key in range(0, customer_df['age'].max() + 1, 5)}
    income_range_slider_min = customer_df['income'].min()
    income_range_slider_max = customer_df['income'].max()
    income_range_slider_value = [customer_df['income'].min(), customer_df['income'].min() + 5000]
    income_range_slider_marks = {int(key): {'label': f"{key}"} for key in
                                 range(0, customer_df['income'].max() + 1, 5000)}
    return country_checkbox_options, gender_checkbox_options, \
    age_range_slider_min, \
    age_range_slider_max, \
    age_range_slider_value, \
    age_range_slider_marks, \
    income_range_slider_min, \
    income_range_slider_max, \
    income_range_slider_value, \
    income_range_slider_marks

@app.callback(
        Output('state_dropdown_modal', 'options'),
        [Input('country_checkbox_modal', 'value')],
        )
def update_state_modal_dropdown(value):
    customer = Customer()
    customer_df = pd.DataFrame(customer.get_customer_data())
    df = customer_df.loc[customer_df['customer_country'].isin(value)]
    states = sorted(df['customer_state'].unique())
    return [
        {'label': f"{brazil_state_code_map[key]}", 'value': key} for key in states
    ]

@app.callback(
        Output('city_dropdown_modal', 'options'),
        [Input('state_dropdown_modal', 'value')],
        )
def update_city_modal_dropdown(value):
    customer = Customer()
    customer_df = pd.DataFrame(customer.get_customer_data())
    unique_cities = customer_df.loc[customer_df['customer_state'].isin(value)]['customer_city'].unique()
    return [
        {'label': f"{key}", 'value': key} for key in unique_cities
    ]

@app.callback(Output('cards-content', 'children'), Output("modal", "is_open"),
              [Input('url', 'href'), Input("open", "n_clicks"), Input("close", "n_clicks")],
              [State("modal", "is_open")])
def display_custom_param_list_page(href, open, close, is_open):
    print('display_custom_param_list_page',href, open, close, is_open)
    cards_list = []
    if is_open is None and href is not None and 'custom_maps_list' == href.split('/')[-1]:
        cards_list = create_custom_params_card_list()

    if is_open is True and close is not None:
        is_open = False
        cards_list = create_custom_params_card_list()
    elif (is_open is False or is_open is None) and open is not None:
        is_open = True


    return cards_list, is_open

def create_custom_params_card_list():
    cards_list = []
    csp = SegmentationParameters()
    custom_params_list = csp.fetch_all_params()
    for index, params in enumerate(custom_params_list):
        card_body = []
        card_body.append(html.P(
            f"No of Segments: {params.get('n_segments')}",
            className="card-text",
        ))
        card_body.append(html.P(
            f"Data period: {params.get('data_period')}",
            className="card-text",
        ))
        segment_separators = params.get('segment_separators', [])
        if len(segment_separators) >= 3 and len(segment_separators)<=10:

            class_name = chr(ord('A') + len(segment_separators) - 1)
            class_ranges = []
            for ind in range(0, len(segment_separators) - 1):
                class_ranges.append(f"Class {class_name}: [{int(segment_separators[ind]*100)} - {int(segment_separators[ind + 1]*100)}]")
                class_name = chr(ord(class_name) - 1)
            class_ranges.append(
                f"Class {chr(ord(class_name))}: [{int(segment_separators[-1] * 100)} - {100}]")
            card_body.append(html.P(
                f"Segment seperators ranges:  {',    '.join(class_ranges)}",
                className="card-text",
            ))

        if params.get('demography') is not None:
            if params['demography'].get('genders') is not None and len(params['demography'].get('genders')) > 0:
                card_body.append(html.P(
                    f"Genders:  {', '.join(params['demography'].get('genders'))}",
                    className="card-text",
                ))
            if params['demography'].get('age_range') is not None and len(params['demography'].get('age_range')) == 2:
                card_body.append(html.P(
                    f"Age range:  min={params['demography'].get('age_range')[0]}, max={params['demography'].get('age_range')[1]}",
                    className="card-text",
                ))
            if params['demography'].get('income_range') is not None and len(
                    params['demography'].get('income_range')) == 2:
                card_body.append(html.P(
                    f"Income range:  min={params['demography'].get('income_range')[0]}, max={params['demography'].get('income_range')[1]}",
                    className="card-text",
                ))

        if params.get('geography') is not None:
            if params['geography'].get('country') is not None and len(params['geography'].get('country')) > 0:
                card_body.append(html.P(
                    f"Countries:  {', '.join(params['geography'].get('country'))}",
                    className="card-text",
                ))
            if params['geography'].get('state') is not None and len(params['geography'].get('state')) > 0:
                card_body.append(html.P(
                    f"States:  {', '.join(params['geography'].get('state'))}",
                    className="card-text",
                ))
            if params['geography'].get('city') is not None and len(params['geography'].get('city')) > 0:
                card_body.append(html.P(
                    f"Cities:  {', '.join(params['geography'].get('city'))}",
                    className="card-text",
                ))

        # card_body.append(dbc.Button("View", id=f"view-btn", color="primary"))
        card_body.append(dcc.Link('View', href=f"/other_dashboard?id={str(params['_id'])}"))
        cards_list.append(dbc.Card(
            [
                dbc.CardHeader([
                    html.H2(
                        dbc.Button(
                            f"{params.get('title')}",
                            color="link",
                            id=f"group-{index + 1}-toggle",
                        ),
                    ),
                    html.Div(id='container-button-timestamp')],
                ),
                dbc.Collapse(
                    dbc.CardBody(card_body),
                    id=f"collapse-{index + 1}",
                )

            ]
        ))
    return cards_list

total_accordians = SegmentationParameters().total_count()

# define callbacks for card accordions with ids collapse-{i}
# print("total", SegmentationParameters().total_count())
for index in range(1, total_accordians+1000):

    @app.callback(
        Output(f"collapse-{index}", "is_open"),
        [Input(f"group-{index}-toggle", "n_clicks")],
        [State(f"collapse-{index}", "is_open")],
    )
    def toggle_collapse(n, is_open):
        print('accordian', index, n, is_open)
        if n:
            return not is_open
        return is_open
