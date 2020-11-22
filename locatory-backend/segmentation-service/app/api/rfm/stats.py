import time
import pandas
import calendar
import numpy as np


def last_day_of_a_month(year, month):
    if calendar.isleap(year):
        feb = 29
    else:
        feb = 28

    if str(month).startswith('0'):
        month = int(str(month).lstrip('0'))

    month_days_dict = {1: 31, 2: feb, 3: 31, 4: 30, 5: 31,
                       6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

    last_day = month_days_dict[month]

    return last_day


def get_last_x_month_from_now(x):
    now = time.localtime()
    # x + 1 to exclude the current month
    list_of_months = [time.localtime(time.mktime(
        (now.tm_year, now.tm_mon - n, 1, 0, 0, 0, 0, 0, 0)))[:2] for n in range(x + 1)][1:]

    return list_of_months[-1:][0]


def get_rfm(conn, cur, max_custs, date_range, df):
    if not date_range:
        query = "SELECT * FROM RFM ORDER BY Customer_ID, Site_Use_ID;"
        ordered_df = pandas.read_sql_query(query, conn)
        results = ordered_df.to_json(orient='records')
    else:
        ordered_df = df.sort_values(by=['Customer_ID', 'Site_Use_ID'])
        results = ordered_df.to_json(orient='records')

    return results
