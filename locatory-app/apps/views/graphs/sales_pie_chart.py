import pandas as pd
import plotly.express as px

"""
This function generated pie chart based on revenue sales by location
"""
def generate_pie_chart_by_location(current_df: pd.DataFrame, type: str):
    df = current_df.copy()
    highest_payment_val = (df['payment_value'].max()) / 4
    fig = px.pie()

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


"""
This function generated pie chart based on revenue sales by product category
"""
def generate_pie_chart_by_product_category(current_df: pd.DataFrame):
    df = current_df.copy()
    highest_payment_val = (df['payment_value'].max()) / 4
    df.loc[df['payment_value'] < highest_payment_val, 'product.category'] = 'Other products'

    fig = px.pie(df, values=df['payment_value'],
                 names=df['product.category'],
                 title='Sales by item category', color_discrete_sequence=px.colors.diverging.Portland)

    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig
