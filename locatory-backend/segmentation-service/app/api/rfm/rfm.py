import stats
import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
from pyclustering.cluster.kmedians import kmedians

from rfm_parameters import RFMParameters
from rfm_database import RFMDatabase


class RFM(RFMParameters):

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
        rfm_df = RFMDatabase.get_instance().get_rfm_dataframe(start_date, end_date)

        datetime_end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        rfm_df['R_Value'] = (
            datetime_end_date - pd.to_datetime(rfm_df['Max_Date'], errors='coerce')).dt.days

        rfm_df.drop(['Max_Date'], axis=1, inplace=True)

        return rfm_df

    def merge_with_duration(self, rfm_df, start_date, end_date):
        # Calc Duration
        datetime_start_date = datetime.datetime.strptime(
            start_date, '%Y-%m-%d')
        datetime_end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        # TODO: Check if Min_Date needs relpacing with start_date for old customers, check Mongo RFM query as well
        rfm_df['Duration_Days'] = (
            datetime_end_date - pd.to_datetime(rfm_df['Min_Date'], errors='coerce')).dt.days

        rfm_df['Duration_Days'] = rfm_df['Duration_Days'].replace(0, 1)

        rfm_df.drop(['Min_Date'], axis=1, inplace=True)

        return rfm_df

    def get_class_kmedians(self, number, medians, key_val):
        # Predict the cluster
        cluster_median = min(medians, key=lambda x: abs(x-number))
        median_score = key_val[str(cluster_median)]
        return median_score

    def get_kmedian_clusters(self, kmedian_medians):
        medians = [x[0] if type(x) == list else x for x in kmedian_medians]

        asc_medians = sorted(medians)

        i = 1
        key_val = {}
        for med in asc_medians:
            key_val[str(med)] = i
            i += 1

        return medians, key_val

    def check_and_get_clusters(self, cluster_for, cluster_type):
        medians = []

        df = pd.read_csv('required_files/kmedian_cluster_centers.csv')

        if not df.empty:
            req_df = df.loc[(df['client_name'] == client_name) & (
                df['cluster_for'] == cluster_for) & (df['cluster_type'] == cluster_type)].reset_index()

            if not req_df.empty:
                for col in req_df.columns.values:
                    if col not in ['index', 'client_name', 'cluster_for', 'cluster_type']:
                        medians.append(req_df.get_value(0, col))

                return True, medians, df

        return False, [], df

    def calculate_and_save_kmedians(self, rfmd_df, col, cluster_type):
        medians = []

        unique_list = list(set(rfmd_df[col].tolist()))

        a = np.array(sorted(unique_list))
        initial_centers = [np.array([np.percentile(a, 2)]), np.array([np.percentile(a, 32)]),
                           np.array([np.percentile(a, 55)]), np.array(
                               [np.percentile(a, 75)]),
                           np.array([np.percentile(a, 98)])]

        data_list = [[data] for data in unique_list]
        kmedians_instance = kmedians(
            data_list, initial_centers, 0.0001, ccore=False)

        # run cluster analysis and obtain results
        kmedians_instance.process()

        medians = kmedians_instance.get_medians()

        kmedian_medians = [x[0] for x in medians]
        asc_medians = sorted(kmedian_medians)

        # Append and Save the new df
        # TODO: save the model

        return medians

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
            m_value = x_df.get_value(i, 'Avg_M_Value')
            r_value = x_df.get_value(i, 'R_Value')
            f_value = x_df.get_value(i, 'Avg_F_Value')
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
        rfmd_df['Avg_M_Value'] = rfmd_df['M_Value']/rfmd_df['Duration_Days']
        rfmd_df['Avg_F_Value'] = rfmd_df['F_Value']/rfmd_df['Duration_Days']

        # TODO: Check datatype of Avg cols
        rfmd_df = rfmd_df.round({'Avg_F_Value': 3, 'Avg_M_Value': 2})

        return rfmd_df

    def cluster_average_rfm_values(self, rfmd_df):
        medians_m = self.calculate_and_save_kmedians(
            rfmd_df, 'Avg_M_Value', 'm')

        medians_f = self.calculate_and_save_kmedians(
            rfmd_df, 'Avg_F_Value', 'f')

        rfmd_df = self.get_rfm_df_with_scores(
            rfmd_df, medians_m, medians_f)

        rfmd_df = rfmd_df.round({'RFM_Score': 2})

        return rfmd_df

    def perform_rfm_segmentation(self, rfm_logger):
        # Default Dates Last 1 year
        cur_date = datetime.datetime.now().date()
        date_before_period = cur_date + \
            relativedelta(months=-self.data_period)

        rfm_df = self.get_base_rfm_df(date_before_period, cur_date)

        rfmd_df = self.merge_with_duration(
            rfm_df, date_before_period, cur_date)

        rfmd_df = self.get_average_rfm_df(rfmd_df)

        rfmd_df = self.cluster_average_rfm_values(rfmd_df)

        return rfmd_df
