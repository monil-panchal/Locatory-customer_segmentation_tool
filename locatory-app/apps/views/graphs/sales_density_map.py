import pandas as pd
import plotly.express as px

mapbox_access_token = 'pk.eyJ1IjoiYWhzLXZhIiwiYSI6ImNraGsyMWVmdDByOWszNnNkdzJqcHpwOWMifQ.llITOAaVvDUflVgenIPPlw'

px.set_mapbox_access_token(mapbox_access_token)


def generate_density_map(current_df: pd.DataFrame):
    df = current_df.copy()
    df['lat-lng'] = current_df['customer.address.co_ordinate.coordinates']

    fig = px.density_mapbox(df, lat=df['lat-lng'].str[1], lon=df['lat-lng'].str[0], z=df['payment_value'], radius=15,
                            mapbox_style='dark',
                            color_continuous_scale='RdYlBu',
                            range_color=[0, df['payment_value'].max()],
                            hover_data=[df['order_id'],
                                        df['payment_value'],
                                        df['order_date'],
                                        df['customer.name'],
                                        df['customer.email'],
                                        df['product.category']]
                            )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig
