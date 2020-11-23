import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt

def generate_bar_line_graph(current_df: pd.DataFrame, prev_df: pd.DataFrame, type: str):

    print(f'type of x axis is: {type}')

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    if type == 'year':
        current_x = current_df['order_date'].dt.month
        # current_x = months
        prev_x = prev_df['order_date'].dt.month
        # prev_x = months

    else:
        current_x = current_df['order_date'].apply(lambda d: (d.day-1) // 7 + 1)
        prev_x = prev_df['order_date'].apply(lambda d: (d.day-1) // 7 + 1)

    print(f'prev_x: {prev_x}')
    print(f'current_x: {current_x}')

    # fig = px.line(current_df, x=current_x, y=list(range(0, current_df.shape[0])), color=px.Constant("This year"),
    #               labels=dict(x="Fruit", y="Amount", color="Time Period"))
    # fig.add_bar(x=prev_x, y=list(range(0, prev_df.shape[0])), name="Last year")
    # fig.show()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=current_x,
        y=list(range(0, current_df.shape[0])),
        name='Current timeline',
        marker_color='indianred'
    ))
    fig.add_trace(go.Bar(
        x=prev_x,
        y=list(range(0, prev_df.shape[0])),
        name='Previous timeline',
        marker_color='lightsalmon'
    ))

    fig.update_layout(barmode='group', xaxis_tickangle=-45)

    return fig