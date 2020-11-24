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

    # fig = px.density_mapbox(df, lat=df['lat-lng'].str[1], lon=df['lat-lng'].str[0], z=df['payment_value'], radius=10,
    #                         mapbox_style="open-street-map")

    fig = px.choropleth_mapbox(df, geojson=gdf["geometry"], color="payment_value",
                               locations="lat-lng", featureidkey="properties.district",
                               mapbox_style="carto-positron", zoom=9)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # fig.show()

    return fig
