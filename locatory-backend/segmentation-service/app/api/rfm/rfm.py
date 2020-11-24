import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd

import app.api.rfm.stats
from .rfm_database import RFMDatabase


class RFM():

    def __init__(self, parameters_dict):
        self.rfm_parameters = parameters_dict

    # Methods for RFM Table
    def get_recency_class(self, r_value):
        if r_value <= 30:
            r_class = 5

        elif r_value > 30 and r_value <= 60:
            r_class = 4

        elif r_value > 60 and r_value <= 90:
            r_class = 3

        elif r_value > 90 and r_value <= 180:
            r_class = 2

        else:
            r_class = 1

        return r_class

    def get_base_rfm_df(self, start_date, end_date):
        rfm_df = RFMDatabase.get_instance().get_rfm_dataframe(
            start_date, end_date, self.rfm_parameters)

        rfm_df['R'] = (
            end_date - pd.to_datetime(rfm_df['Latest_Order_Date'], errors='coerce')).dt.days

        rfm_df.drop(['Latest_Order_Date'], axis=1, inplace=True)

        return rfm_df

    def merge_with_duration(self, rfm_df, end_date):
        # Calc Duration
        # TODO: Check if Min_Date needs relpacing with start_date for old customers, check Mongo RFM query as well
        rfm_df['Duration_Days'] = (
            end_date - pd.to_datetime(rfm_df['First_Order_Date'], errors='coerce')).dt.days

        rfm_df['Duration_Days'] = rfm_df['Duration_Days'].replace(0, 1)

        rfm_df.drop(['First_Order_Date'], axis=1, inplace=True)

        return rfm_df

    def assign_rfm_class(self, score, df, i, col):
        if score <= 0.2:
            df.set_value(i, col, 'E')

        elif score > 0.2 and score <= 0.4:
            df.set_value(i, col, 'D')

        elif score > 0.4 and score <= 0.6:
            df.set_value(i, col, 'C')

        elif score > 0.6 and score <= 0.8:
            df.set_value(i, col, 'B')

        else:
            df.set_value(i, col, 'A')

        return df

    def get_rfm_df_with_scores(self, x_df, medians_m, medians_f, req):
        x_df['R_Score'] = 0
        x_df['F_Score'] = 0
        x_df['M_Score'] = 0

        # if req != 'insights':
        x_df['Duration_Score'] = 0

        x_df['RFM_Score'] = 0.0
        x_df['Reliability'] = 0.0

        final_medians_m, key_val_m = self.get_kmedian_clusters(medians_m)
        final_medians_f, key_val_f = self.get_kmedian_clusters(medians_f)

        for i in range(len(x_df)):
            m_value = x_df.get_value(i, 'Avg_M')
            r_value = x_df.get_value(i, 'R')
            f_value = x_df.get_value(i, 'Avg_F')
            pv_value = x_df.get_value(i, 'PV_Ratio')
            dur_value = x_df.get_value(i, 'Duration_Days')

            # Recency Score
            r_class = self.get_recency_class(r_value)
            x_df.set_value(i, 'R_Score', r_class)

            # Frequency Score
            f_class = self.get_class_kmedians(
                f_value, final_medians_f, key_val_f)
            x_df.set_value(i, 'F_Score', f_class)

            # Monetary Score
            m_class = self.get_class_kmedians(
                m_value, final_medians_m, key_val_m)
            x_df.set_value(i, 'M_Score', m_class)

            score = float(int(r_class) + int(f_class) + int(m_class))/float(15)
            x_df.set_value(i, 'RFM_Score', score)

            x_df = self.assign_rfm_class(score, x_df, i, 'RFM_Label')

        return x_df

    def get_average_rfm_df(self, rfmd_df):
        rfmd_df['Avg_M'] = rfmd_df['M']/rfmd_df['Duration_Days']
        rfmd_df['Avg_F'] = rfmd_df['F']/rfmd_df['Duration_Days']

        # TODO: Check datatype of Avg cols
        rfmd_df = rfmd_df.round({'Avg_F': 3, 'Avg_M': 2})

        return rfmd_df

    def fix_outliers(self, df, column):
        df_copy = df.copy()

        # Ref: https://app.pluralsight.com/guides/cleaning-up-data-from-outliers
        # Finding outliers
        quartile1 = df[column].quantile(0.25)
        quartile3 = df[column].quantile(0.75)
        inter_quartile_range = quartile3 - quartile1

        df_copy["Is_Outlier"] = (df_copy[column] < (quartile1 - 1.5 * inter_quartile_range)
                                 ) | (df_copy[column] > (quartile3 + 1.5 * inter_quartile_range))

        # Dropping outliers
        df_copy = df_copy.loc[(df_copy["Is_Outlier"] != True)]
        df_copy.drop("Is_Outlier", axis=1, inplace=True)

        return df_copy

    def cluster_average_rfm_values(self, rfmd_df):
        medians_m = self.calculate_and_save_kmedians(
            rfmd_df, 'Avg_M', 'm')

        medians_f = self.calculate_and_save_kmedians(
            rfmd_df, 'Avg_F', 'f')

        # rfmd_df = self.get_rfm_df_with_scores(
        #     rfmd_df, medians_m, medians_f)

        # rfmd_df = rfmd_df.round({'RFM_Score': 2})

        return rfmd_df

    def perform_rfm_segmentation(self, rfm_logger):
        # Default Dates Last 1 year
        cur_date = datetime.datetime.now()
        date_before_period = cur_date + \
            relativedelta(months=-self.rfm_parameters.get("data_period"))

        rfm_df = self.get_base_rfm_df(date_before_period, cur_date)

        rfm_df = self.merge_with_duration(rfm_df, cur_date)

        rfm_df = self.get_average_rfm_df(rfm_df)
        print(rfm_df.head())
        rfm_df = self.cluster_average_rfm_values(rfm_df)

        # return rfmd_df
        return True
