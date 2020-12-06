import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd

from .rfm_database import RFMDatabase
from .clustering import Clustering


class RFM():

    def __init__(self, parameters_dict, document_id):
        self.rfm_parameters = parameters_dict
        self.document_id = document_id

    # Methods for RFM Table

    def get_base_rfm_df(self, start_date, end_date):
        rfm_df = RFMDatabase.get_instance().get_rfm_dataframe(
            start_date, end_date, self.rfm_parameters)

        if rfm_df.empty:
            return rfm_df

        rfm_df['R'] = (
            end_date - pd.to_datetime(rfm_df['Latest_Order_Date'], errors='coerce')).dt.days

        rfm_df.drop(['Latest_Order_Date'], axis=1, inplace=True)

        return rfm_df

    def merge_with_duration(self, rfm_df, end_date):
        # Calc Duration
        rfm_df['Duration_Days'] = (
            end_date - pd.to_datetime(rfm_df['First_Order_Date'], errors='coerce')).dt.days

        rfm_df['Duration_Days'] = rfm_df['Duration_Days'].replace(0, 1)

        rfm_df.drop(['First_Order_Date'], axis=1, inplace=True)

        return rfm_df

    def set_recency_scores(self, df):
        # Recency score will always be in between 1 to 5
        df.loc[(df["R"] <= 30), 'R_Score'] = 5
        df.loc[((df["R"] > 30) & (df["R"] <= 60)), 'R_Score'] = 4
        df.loc[((df["R"] > 60) & (df["R"] <= 90)), 'R_Score'] = 3
        df.loc[((df["R"] > 90) & (df["R"] <= 180)), 'R_Score'] = 2
        df.loc[(df["R"] > 180), 'R_Score'] = 1

        # Convert R_Score to integer
        df["R_Score"] = df["R_Score"].astype(int)

        return df

    def assign_rfm_labels(self, df):
        # Max 10 labels because n_segments falls between 3 and 10
        possible_labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

        n_segments = self.rfm_parameters.get("n_segments")
        possible_labels = possible_labels[:n_segments]
        segment_separators = self.rfm_parameters.get("segment_separators")

        if not segment_separators:
            part_duration = 1 / n_segments
            segment_separators = [
                round(i * part_duration, 2) for i in range(n_segments)]

        for idx, segment_start in enumerate(segment_separators[:-1]):
            df.loc[((df["RFM_Score"] >= segment_start) & (
                df["RFM_Score"] < segment_separators[idx+1])), 'RFM_Label'] = possible_labels[n_segments-1-idx]

        # Adding last label - A class
        df.loc[(df["RFM_Score"] >= segment_separators[-1]),
               'RFM_Label'] = possible_labels[0]

        return df

    def get_rfm_df_with_scores(self, df):
        n_segments = self.rfm_parameters.get("n_segments")

        # Setting Recency scores - Monetary and Frequency scores were already set during clustering
        df = self.set_recency_scores(df)

        # Setting RFM scores and labels
        df["RFM_Score"] = (df["R_Score"] + df["Avg_M_Score"] +
                           df["Avg_F_Score"])/float((n_segments*2) + 5)
        df = df.round({'RFM_Score': 3})
        df = self.assign_rfm_labels(df)

        return df

    def get_average_rfm_df(self, rfmd_df):
        rfmd_df['Avg_M'] = rfmd_df['M']/rfmd_df['Duration_Days']
        rfmd_df['Avg_F'] = rfmd_df['F']/rfmd_df['Duration_Days']

        rfmd_df = rfmd_df.round({'Avg_F': 3, 'Avg_M': 2})

        return rfmd_df

    def cluster_average_rfm_values(self, rfmd_df):
        rfmd_df = Clustering.get_instance().get_kmeans_clustered_df(
            rfmd_df, 'Avg_M', 'm', self.document_id, self.rfm_parameters.get("n_segments"))

        rfmd_df = Clustering.get_instance().get_kmeans_clustered_df(
            rfmd_df, 'Avg_F', 'f', self.document_id, self.rfm_parameters.get("n_segments"))

        rfmd_df = self.get_rfm_df_with_scores(rfmd_df)

        return rfmd_df

    def perform_rfm_segmentation(self, rfm_logger):
        # Default Dates Last 1 year
        cur_date = datetime.datetime.now()
        date_before_period = cur_date + \
            relativedelta(months=-self.rfm_parameters.get("data_period"))

        rfm_df = self.get_base_rfm_df(date_before_period, cur_date)
        if not rfm_df.empty:
            rfm_df = self.merge_with_duration(rfm_df, cur_date)

            rfm_df = self.get_average_rfm_df(rfm_df)

            rfm_df = self.cluster_average_rfm_values(rfm_df)

        return rfm_df, date_before_period, cur_date
