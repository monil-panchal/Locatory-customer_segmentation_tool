import calendar
import pandas as pd

"""
This is a utility method for adding months and weeks as new columns in the existing data_preprocessor based on the date field.
"""


def add_month_week(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    if not df.empty:
        if col_name in df.columns:
            df['month'] = df[col_name].dt.month
            df['month'] = df['month'].apply(lambda x: calendar.month_abbr[x])
            df['month'] = pd.Categorical(df['month'], categories=months, ordered=True)
            df.sort_values('month')

            df['week'] = df[col_name].apply(lambda d: (d.day - 1) // 7 + 1)

    return df
