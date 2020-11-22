import stats
import datetime
import numpy as np
import pandas as pd
from pyclustering.cluster.kmedians import kmedians

from rfm_parameters import RFMParameters


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

    def get_base_rfm_df(self, bq_db, client_name, start_date, end_date, vans):
        rfm_df = db_functions.get_query_df(bq_db, query)
        datetime_end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        rfm_df['R_Value'] = (
            datetime_end_date - pandas.to_datetime(rfm_df['Max_Date'], errors='coerce')).dt.days
        # rfm_df['R_Value'] = (pandas.datetime.now().date() - pandas.to_datetime(rfm_df['Max_Date'], errors='coerce')).dt.days
        rfm_df.drop(['Max_Date'], axis=1, inplace=True)

        return rfm_df

    def merge_with_duration(self, rfm_pv_df, req, start_date, end_date):
        # Calc Duration
        datetime_start_date = datetime.datetime.strptime(
            start_date, '%Y-%m-%d')
        datetime_end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        if req == 'insights':
            rfm_pv_df['Duration_Days'] = (
                datetime_end_date - datetime_start_date).days
            rfm_pv_df['Duration_Days'] = rfm_pv_df['Duration_Days'].replace(
                0, 1)
        else:
            # rfm_pv_df['Duration_Days'] = (pandas.datetime.now().date() - pandas.to_datetime(rfm_pv_df['Min_Date'], errors='coerce')).dt.days
            rfm_pv_df['Duration_Days'] = (
                datetime_end_date - pandas.to_datetime(rfm_pv_df['Min_Date'], errors='coerce')).dt.days
            rfm_pv_df['Duration_Days'] = rfm_pv_df['Duration_Days'].replace(
                0, 1)

        rfm_pv_df.drop(['Min_Date'], axis=1, inplace=True)

        return rfm_pv_df

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

    def check_and_get_clusters(self, client_name, cluster_for, cluster_type, setting_paths):
        medians = []

        df = pandas.read_csv(
            setting_paths['required_files']+'required_files/kmedian_cluster_centers.csv')

        if not df.empty:
            req_df = df.loc[(df['client_name'] == client_name) & (
                df['cluster_for'] == cluster_for) & (df['cluster_type'] == cluster_type)].reset_index()

            if not req_df.empty:
                for col in req_df.columns.values:
                    if col not in ['index', 'client_name', 'cluster_for', 'cluster_type']:
                        medians.append(req_df.get_value(0, col))

                return True, medians, df

        return False, [], df

    def calculate_and_save_kmedians(self, client_name, data_list, cluster_for, cluster_type, setting_paths, req):
        medians = []
        chk = False

        if req != 'insights':
            chk, medians, df = self.check_and_get_clusters(
                client_name, cluster_for, cluster_type, setting_paths)

        if not chk:
            unique_list = list(set(data_list))
            data_list = [[data] for data in data_list]

            a = np.array(sorted(unique_list))
            initial_centers = [array([np.percentile(a, 2)]), array([np.percentile(a, 32)]), array([np.percentile(a, 55)]),
                               array([np.percentile(a, 75)]), array([np.percentile(a, 98)])]

            kmedians_instance = kmedians(
                data_list, initial_centers, 0.0001, ccore=False)

            # run cluster analysis and obtain results
            kmedians_instance.process()

            medians = kmedians_instance.get_medians()

            kmedian_medians = [x[0] for x in medians]
            asc_medians = sorted(kmedian_medians)

            # Append and Save the new df
            if req != 'insights':
                df_len = len(df)

                df.set_value(df_len, 'client_name', client_name)
                df.set_value(df_len, 'cluster_for', cluster_for)
                df.set_value(df_len, 'cluster_type', cluster_type)
                df.set_value(df_len, '1', asc_medians[0])
                df.set_value(df_len, '2', asc_medians[1])
                df.set_value(df_len, '3', asc_medians[2])
                df.set_value(df_len, '4', asc_medians[3])
                df.set_value(df_len, '5', asc_medians[4])

                df.to_csv(setting_paths['required_files'] +
                          'required_files/kmedian_cluster_centers.csv', index=False)

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
        x_df['PV_Score'] = 0

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

            # PV Score
            x_df = self.get_pv_score(pv_value, x_df, i)

            # Duration Score
            # if req != 'insights':
            x_df = self.get_duration_score(dur_value, x_df, i)

            score = float(int(r_class) + int(f_class) + int(m_class))/float(15)
            x_df.set_value(i, 'RFM_Score', score)
            x_df.set_value(i, 'Reliability', float(int(r_class) + int(f_class) +
                                                   int(m_class) + int(x_df.get_value(i, 'Duration_Score')))/float(20))

            x_df = self.assign_rfm_class(score, x_df, i, 'RFM_Label')

        return x_df

    def get_average_lrfm_df(self, client_name, lrfm_df, setting_paths, req):
        lrfm_df['Avg_M_Value'] = lrfm_df['M_Value']/lrfm_df['Duration_Days']
        lrfm_df['Avg_F_Value'] = lrfm_df['F_Value']/lrfm_df['Duration_Days']

        if lrfm_df['Avg_M_Value'].dtype == 'O':
            lrfm_df['Avg_M_Value'] = lrfm_df['Avg_M_Value'].astype('float64')
        lrfm_df = lrfm_df.round({'Avg_F_Value': 3, 'Avg_M_Value': 2})

        # RFM Analysis
        # kmeans_m, kmeans_f = get_f_m_clusters(lrfm_df['Avg_M_Value'].tolist(), lrfm_df['Avg_F_Value'].tolist())
        m_list = [0 if i < 0 else i for i in lrfm_df['Avg_M_Value'].tolist()]

        medians_m = self.calculate_and_save_kmedians(
            client_name, m_list, 'customers', 'm', setting_paths, req)
        medians_f = self.calculate_and_save_kmedians(
            client_name, lrfm_df['Avg_F_Value'].tolist(), 'customers', 'f', setting_paths, req)
    #     lrfm_df = get_df_with_rfm(lrfm_df, kmeans_m, kmeans_f)
        lrfm_df = self.get_rfm_df_with_scores(
            lrfm_df, medians_m, medians_f, req)
        lrfm_df = lrfm_df.round({'RFM_Score': 2, 'Reliability': 3})
        return lrfm_df

    def get_average_lrsm_df(self, client_name, lrsm_df, setting_paths, req):
        lrsm_df['Avg_M_Value'] = lrsm_df['M_Value']/lrsm_df['Duration_Days']
        lrsm_df['Avg_S_Value'] = lrsm_df['S_Value']/lrsm_df['Duration_Days']

        if lrsm_df['Avg_M_Value'].dtype == 'O':
            lrsm_df['Avg_M_Value'] = lrsm_df['Avg_M_Value'].astype('float64')

        lrsm_df = lrsm_df.round({'Avg_S_Value': 2, 'Avg_M_Value': 2})

        # RFM Analysis
        # kmeans_m, kmeans_f = get_f_m_clusters(lrsm_df['Avg_M_Value'].tolist(), lrsm_df['Avg_S_Value'].tolist())
        m_list = [0 if i < 0 else i for i in lrsm_df['Avg_M_Value'].tolist()]

        medians_m = self.calculate_and_save_kmedians(
            client_name, m_list, 'products', 'm', setting_paths, req)
        medians_f = self.calculate_and_save_kmedians(
            client_name, lrsm_df['Avg_S_Value'].tolist(), 'products', 'f', setting_paths, req)

        lrsm_df = self.get_rsm_df_with_scores(
            lrsm_df, medians_m, medians_f, req)
        lrsm_df = lrsm_df.round({'RSM_Score': 2, 'Reliability': 3})
        return lrsm_df

    def table_rows_check(self, table_name, cur):
        query = """select R_Score, M_Score FROM """ + \
            str(table_name)+""" LIMIT 5;"""

        rows = self.run_query_get_all_rows(query, cur)

        if rows:
            return True
        else:
            return False

    def calculate_default_rfm(self, rfm_logger):
        # Default Dates Last 1 year
        cur_date = datetime.datetime.now().date()
        start_year, start_month = stats.get_last_x_month_from_now(12)
        start_day = stats.last_day_of_a_month(start_year, start_month)

        start_date = str(start_year)+'-'+str(start_month)+'-01'

        end_date = str(cur_date.year)+'-' + \
            str(cur_date.month)+'-'+str(cur_date.day)

        rfm_df = self.get_base_rfm_df(start_date, end_date)

        rfmd_df = self.merge_with_duration(rfm_df, start_date, end_date)

        avg_lrfm_df = self.get_average_lrfm_df(client_name, lrfm_df)

        return avg_lrfm_df, 'success'

    def calculate_rfm_by_dates(self, bq_db, client_name, start_date, end_date, vans, ins_logger, setting_paths, req):
        rfm_df = self.get_base_rfm_df(
            bq_db, client_name, start_date, end_date, vans)

        rfm_pv_df = self.get_rfm_df_with_pvratio(
            rfm_df, bq_db, client_name, start_date, end_date, vans)

        lrfm_df = self.merge_with_duration(
            rfm_pv_df, req, start_date, end_date)

        avg_lrfm_df = self.get_average_lrfm_df(
            client_name, lrfm_df, setting_paths, req)

        # avg_lrfm_df.to_csv('rfm_date.csv', index=False)

        return avg_lrfm_df
