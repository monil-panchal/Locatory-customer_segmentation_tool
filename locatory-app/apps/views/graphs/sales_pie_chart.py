import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def generate_pie_chart_by_location(current_df: pd.DataFrame, type: str):
    fig = go.Figure()
    print(f'pie chart type is: {type}')

    if type == 'country':
        fig = px.pie(current_df, values=current_df['payment_value'],
                     names=current_df['customer.address.customer_state'],
                     title='Sales by state/province')
    elif type == 'state':
        fig = px.pie(current_df, values=current_df['payment_value'], names=current_df['customer.address.customer_city'],
                     title='Sales by cities')

    elif type == 'city':
        fig = px.pie(current_df, values=current_df['payment_value'], names=current_df['customer.address.zip_code'],
                     title='Sales by area/zip_code')

    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig
