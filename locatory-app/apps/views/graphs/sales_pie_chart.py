import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def generate_pie_chart_by_location(current_df: pd.DataFrame, type: str):
    df = current_df.copy()
    highest_payment_val = (df['payment_value'].max()) / 4

    # df = current_df.nlargest(10, 'payment_value').copy()

    fig = px.pie()
    print(f'pie chart type is: {type}')

    if type == 'country':
        df.loc[df['payment_value'] < highest_payment_val, 'customer.address.customer_state'] = 'Other states'
        fig = px.pie(df, values=df['payment_value'],
                     names=df['customer.address.customer_state'],
                     title='Sales by state/province',
                     color_discrete_sequence=px.colors.diverging.Spectral
                     )
    elif type == 'state':
        df.loc[df['payment_value'] < highest_payment_val, 'customer.address.customer_city'] = 'Other cities'
        fig = px.pie(df, values=df['payment_value'], names=df['customer.address.customer_city'],
                     title='Sales by cities',
                     color_discrete_sequence=px.colors.diverging.Spectral)

    elif type == 'city':
        df.loc[df['payment_value'] < highest_payment_val, 'customer.address.zip_code'] = 'Other zip_codes'
        fig = px.pie(df, values=df['payment_value'], names=df['customer.address.zip_code'],
                     title='Sales by area/zip_code',
                     color_discrete_sequence=px.colors.diverging.Spectral)

    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig


def generate_pie_chart_by_product_category(current_df: pd.DataFrame):
    # df = current_df.nlargest(10, 'payment_value').copy()
    df = current_df.copy()
    highest_payment_val = (df['payment_value'].max()) / 4
    df.loc[df['payment_value'] < highest_payment_val, 'product.category'] = 'Other products'

    fig = px.pie(df, values=df['payment_value'],
                 names=df['product.category'],
                 title='Sales by item category', color_discrete_sequence=px.colors.diverging.Portland)

    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig
