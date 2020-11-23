import pandas as pd
import plotly.graph_objects as go


def generate_bar_line_graph(current_df: pd.DataFrame, prev_df: pd.DataFrame, type: str):
    fig = go.Figure()
    # show month wise data for selected year

    if type == 'year':

        current_month_orders = current_df.groupby(['month'], sort=False).size().reset_index(name='orders')

        fig.add_trace(go.Bar(
            x=current_month_orders['month'],
            y=current_month_orders['orders'],
            name='This year',
            marker_color='rgb(55, 83, 109)'

        ))

        if not prev_df.empty:
            previous_month_orders = prev_df.groupby(['month'], sort=False).size().reset_index(name='orders')

            fig.add_trace(go.Bar(
                x=previous_month_orders['month'],
                y=previous_month_orders['orders'],
                name='Previous year',
                marker_color='rgb(26, 118, 255)'

            ))

        fig.update_layout(xaxis_title='Months')

    else:

        current_week_orders = current_df.groupby(['week']).size().reset_index(name='orders')
        current_week_orders = current_week_orders.sort_values(by=['week'])

        fig.add_trace(go.Bar(
            x=current_week_orders['week'],
            y=current_week_orders['orders'],
            name='This month',
            marker_color='rgb(55, 83, 109)'
        ))

        if not prev_df.empty:
            previous_week_orders = prev_df.groupby(['week']).size().reset_index(name='orders')
            previous_week_orders = previous_week_orders.sort_values(by=['week'])

            fig.add_trace(go.Bar(
                x=previous_week_orders['week'],
                y=previous_week_orders['orders'],
                name='Previous month',
                marker_color='rgb(26, 118, 255)'
            ))

        fig.update_layout(xaxis_title='Weeks',
                          barmode='group',
                          bargap=0.15,
                          bargroupgap=0.1)

    fig.update_layout(
        title='Month/week wise comparison by number of orders',
        yaxis_title='Number of orders',
        barmode='group',
        xaxis_tickangle=-45
    )

    return fig
