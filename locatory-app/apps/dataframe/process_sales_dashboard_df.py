import pandas as pd
import datetime as dt
import calendar

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def add_year_month_week(current_df: pd.DataFrame, previous_df: pd.DataFrame):
    if not current_df.empty:
        if 'order_date' in current_df.columns:
            current_df['month'] = current_df['order_date'].dt.month
            current_df['month'] = current_df['month'].apply(lambda x: calendar.month_abbr[x])
            current_df['week'] = current_df['order_date'].apply(lambda d: (d.day - 1) // 7 + 1)

            current_df['month'] = pd.Categorical(current_df['month'], categories=months, ordered=True)
            current_df.sort_values('month')

    if not previous_df.empty:
        if 'order_date' in previous_df.columns:
            previous_df['month'] = previous_df['order_date'].dt.month
            previous_df['month'] = previous_df['month'].apply(lambda x: calendar.month_abbr[x])
            previous_df['week'] = previous_df['order_date'].apply(lambda d: (d.day - 1) // 7 + 1)

            previous_df['month'] = pd.Categorical(previous_df['month'], categories=months, ordered=True)
            previous_df.sort_values('month')

    return current_df, previous_df