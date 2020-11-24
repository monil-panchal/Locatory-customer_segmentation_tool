import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import geopandas


def generate_density_map(current_df: pd.DataFrame):
    df = current_df.copy()
    df['lat-lng'] = current_df['customer.address.co_ordinate.coordinates']

    print(f'lat-lng df: {df.to_string()}')

    print(df['lat-lng'].str[1])
    print(df['lat-lng'].str[0])

    gdf = geopandas.GeoDataFrame(
        df, geometry=geopandas.points_from_xy(df['lat-lng'].str[0], df['lat-lng'].str[1]))

    print(gdf.head())

    fig = px.density_mapbox(df, lat=df['lat-lng'].str[1], lon=df['lat-lng'].str[0], z=df['payment_value'], radius=15,
                            mapbox_style="open-street-map", range_color=[0, df['payment_value'].max()])
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # fig = px.choropleth_mapbox(gdf, geojson=gdf.geometry, color="payment_value",
    #                            locations="customer.address.customer_city", featureidkey="properties.district",
    #                            mapbox_style="carto-positron", zoom=9)
    # fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # fig = go.Figure(data=go.Scattergeo(
    #     lon=df['lat-lng'].str[0],
    #     lat=df['lat-lng'].str[1],
    #     # text=df['text'],
    #     mode='markers',
    #     marker=dict(
    #         size=8,
    #         opacity=0.8,
    #         reversescale=True,
    #         autocolorscale=False,
    #         symbol='square',
    #         line=dict(
    #             width=1,
    #             color='rgba(102, 102, 102)'
    #         ),
    #         colorscale='Blues',
    #         cmin=0,
    #         color=df['payment_value'],
    #         cmax=df['payment_value'].max(),
    #         colorbar_title="Incoming flights<br>February 2011"
    #     )))
    #
    # fig.update_layout(
    #     title='Most trafficked US airports<br>(Hover for airport names)',
    #     geo=dict(
    #         scope='south america',
    #         # projection_type='albers usa',
    #         showland=True,
    #         landcolor="rgb(250, 250, 250)",
    #         subunitcolor="rgb(217, 217, 217)",
    #         countrycolor="rgb(217, 217, 217)",
    #         countrywidth=0.5,
    #         subunitwidth=0.5
    #     ),
    # )
    # fig.show()

    # fig.show()

    return fig
