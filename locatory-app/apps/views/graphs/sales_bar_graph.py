import pandas as pd
import plotly.graph_objects as go


def generate_bar_graph_by_orders(current_df: pd.DataFrame, prev_df: pd.DataFrame, type: str):
    fig = go.Figure()
    # show month wise data for selected year

    if type == 'year':

        if not current_df.empty:
            current_month_orders = current_df.groupby(['month'], sort=False).size().reset_index(name='orders')

            fig.add_trace(go.Bar(
                x=current_month_orders['month'],
                y=current_month_orders['orders'],
                name='This year',
                marker_color='rgb(55, 83, 109)',
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

        if not current_df.empty:
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


def generate_bar_graph_by_sales(current_df: pd.DataFrame, prev_df: pd.DataFrame, type: str):
    fig = go.Figure()
    # show month wise data for selected year

    if type == 'year':

        if not current_df.empty:
            current_df_sales = current_df[['month', 'payment_value']].copy()
            current_month_orders = current_df_sales.groupby(['month'], sort=False).sum().reset_index()
            print(f'current_month_orders: {current_month_orders}')

            fig.add_trace(go.Bar(
                x=current_month_orders['month'],
                y=current_month_orders['payment_value'],
                name='This year',
                marker_color='#267326'

            ))

        if not prev_df.empty:
            prev_df_sales = prev_df[['month', 'payment_value']].copy()
            prev_month_orders = prev_df_sales.groupby(['month'], sort=False).sum().reset_index()
            print(f'prev_month_orders: {prev_month_orders}')

            fig.add_trace(go.Bar(
                x=prev_month_orders['month'],
                y=prev_month_orders['payment_value'],
                name='Previous year',
                marker_color='#33cc33'

            ))

        fig.update_layout(xaxis_title='Months')

    else:

        if not current_df.empty:
            current_df_sales = current_df[['week', 'payment_value']].copy()
            current_week_orders = current_df_sales.groupby(['week']).sum().reset_index()
            current_week_orders = current_week_orders.sort_values(by=['week'])
            print(f'current_week_orders: {current_week_orders}')

            fig.add_trace(go.Bar(
                x=current_week_orders['week'],
                y=current_week_orders['payment_value'],
                name='This month',
                marker_color='#267326'
            ))

        if not prev_df.empty:
            prev_df_sales = prev_df[['week', 'payment_value']].copy()
            previous_week_orders = prev_df_sales.groupby(['week']).sum().reset_index()
            previous_week_orders = previous_week_orders.sort_values(by=['week'])
            print(f'previous_week_orders: {previous_week_orders}')

            fig.add_trace(go.Bar(
                x=previous_week_orders['week'],
                y=previous_week_orders['payment_value'],
                name='Previous month',
                marker_color='#33cc33'
            ))

        fig.update_layout(xaxis_title='Weeks',
                          barmode='group',
                          bargap=0.15,
                          bargroupgap=0.1)

    fig.update_layout(
        title='Month/week wise comparison by sales in $',
        yaxis_title='Order value in $',
        barmode='group',
        xaxis_tickangle=-45
    )

    return fig
