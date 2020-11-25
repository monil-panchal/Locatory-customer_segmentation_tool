import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def generate_pie_chart_by_location(current_df: pd.DataFrame, type: str):
    df = current_df.nlargest(10, 'payment_value').copy()

    fig = px.pie()
    print(f'pie chart type is: {type}')

    if type == 'country':
        fig = px.pie(df, values=df['payment_value'],
                     names=df['customer.address.customer_state'],
                     title='Sales by state/province (top 10)')
    elif type == 'state':
        fig = px.pie(df, values=df['payment_value'], names=df['customer.address.customer_city'],
                     title='Sales by cities (top 10)')

    elif type == 'city':
        fig = px.pie(df, values=df['payment_value'], names=df['customer.address.zip_code'],
                     title='Sales by area/zip_code (top 10)')

    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig


def generate_pie_chart_by_product_category(current_df: pd.DataFrame):
    df = current_df.nlargest(10, 'payment_value').copy()

    fig = px.pie(df, values=df['payment_value'],
                 names=df['product.category'],
                 title='Sales by item category (top 10)')

    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig
