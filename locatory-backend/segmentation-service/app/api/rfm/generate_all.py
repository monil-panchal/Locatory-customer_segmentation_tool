import math
import timeit
import pandas
import sqlite3
import calendar
import datetime
import collections
import numpy as np
import db_functions
import route_generator
from rfm import RFMRSM
from numpy import array
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from collections import OrderedDict
from datetime import timedelta
from pyclustering.cluster.kmedians import kmedians
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer

# Load static paths
from static_paths import get_static_paths
setting_paths = get_static_paths('dev')

def is_van_route_freq_possible(bq_db, van, client_name):
    query = """select min(Creation_Date) as Min_Date
                from route_recommendation_data.TBL_Sales_Returns_"""+str(client_name)+"""
                where Van_No = '"""+van+"""';"""

    dur_df = db_functions.get_query_df(bq_db, query)
    dur_df['Duration'] = (pandas.datetime.now().date() - pandas.to_datetime(dur_df['Min_Date'], errors='coerce')).dt.days

    try:
        if pandas.notnull(dur_df.get_value(0, 'Duration')) and dur_df.get_value(0, 'Duration') >= 365:
            return True
        else:
            return False
    except:
        return False

def table_rows_check(table_name, cur):
    query = """select R_Score, M_Score FROM """+str(table_name)+""" LIMIT 5;"""

    rows = db_functions.run_query_get_all_rows(query, cur)

    if rows:
        return True
    else:
        return False

# Functions for Frequency Table
def get_van_wise_df(van_id, bq_db, client_name):
    query = """select DISTINCT Customer_ID, Site_Use_ID, Creation_Date, Orig_Sys_Document_Ref from route_recommendation_data.TBL_Sales_Returns_"""+str(client_name)+"""
            where Van_No = '"""+str(van_id)+"""'"""

    van_df = db_functions.get_query_df(bq_db, query)
    van_df['Creation_Date'] = pandas.to_datetime(van_df['Creation_Date'])

    return van_df

# Get day occurence number by month
def get_mdo_df(vanx_df):
    vanx_df['Day'] = vanx_df['Creation_Date'].dt.day
    vanx_df['Day_Occurence'] = 0
    vanx_df['Day_Occurence'] = vanx_df['Day']/7
    vanx_df['Day_Occurence'] = vanx_df['Day_Occurence'].apply(np.ceil).astype('int64')
    vanx_df['Month'] = vanx_df['Creation_Date'].dt.month
    vanx_df['Day'] = vanx_df['Creation_Date'].dt.weekday_name

    # Final Column
    vanx_df["Month_Day_Occurence"] = vanx_df["Month"].map(str) + "_" + vanx_df["Day"].map(str) + "_" + vanx_df["Day_Occurence"].map(str)
    return vanx_df

def get_do_df(vanx_df):
    vanx_df['Day'] = vanx_df['Creation_Date'].dt.day
    vanx_df['Day_Occurence'] = 0
    vanx_df['Day_Occurence'] = vanx_df['Day']/7
    vanx_df['Day_Occurence'] = vanx_df['Day_Occurence'].apply(np.ceil).astype('int64')
    vanx_df['Day'] = vanx_df['Creation_Date'].dt.weekday_name

    # Final Column
    vanx_df["Day_Occurence"] = vanx_df["Day"].map(str) + "_" + vanx_df["Day_Occurence"].map(str)
    return vanx_df

def check_if_day_exists(year, month, day, occ):
    day_map = {'Monday':0, 'Tuesday':1, 'Wednesday':2, 'Thursday':3, 'Friday':4, 'Saturday':5, 'Sunday':6}
    index = day_map[day]
    days = [calendar.weekday(year, month, d) for d in range(1, calendar.monthrange(year, month)[1]+1)]
    count_dict = dict((collections.Counter(days)))
    if occ <= count_dict[index]:
        return True

    return False

def get_overall_mdo(mdo, start_date, temp_dict):
    month_map = {'1':'Jan', '2':'Feb', '3':'Mar', '4':'Apr', '5':'May', '6':'Jun', '7':'Jul', '8':'Aug', '9':'Sep', '10':'Oct', '11':'Nov', '12':'Dec'}
    
    if mdo in temp_dict.keys():
        return temp_dict[mdo], temp_dict
    
    else:
        count = 0
        m,d,o = mdo.split('_')
        dates = [start_date.strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')]
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
        months = list(OrderedDict(((start + timedelta(_)).strftime(r"%b-%y"), None) for _ in range((end - start).days)).keys())

        for month in months:
            if month.split('-')[0] == month_map[m]:
                if int(o) > 4:
                    ch = check_if_day_exists(int('20'+month.split('-')[1]), int(str(m).lstrip('0')), d, int(o))
                    if ch:
                        count += 1
                else:
                    count += 1

        temp_dict[mdo] = count
        return count, temp_dict

def get_overall_do(do, cust_id, site_id, start_date, temp_dict):
    month_map = {'Jan': '1', 'Feb':'2', 'Mar':'3', 'Apr':'4', 'May':'5', 'Jun':'6', 'Jul':'7', 'Aug':'8', 'Sep':'9', 'Oct':'10', 'Nov':'11', 'Dec':'12'}
    cust_do = cust_id+'_'+site_id+'_'+do
    
    if cust_do in temp_dict.keys():
        return temp_dict[cust_do], temp_dict
    else:
        count = 0
        d,o = do.split('_')
        dates = [start_date.strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')]
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
        months = list(OrderedDict(((start + timedelta(_)).strftime(r"%b-%y"), None) for _ in range((end - start).days)).keys())

        for month in months:
    #         if month.split('-')[0] == month_map[m]:
            if int(o) > 4:
                ch = check_if_day_exists(int('20'+month.split('-')[1]), int(month_map[month.split('-')[0]]), d, int(o))
                if ch:
                    count += 1
            else:
                count += 1

        temp_dict[cust_do] = count
        
        return count, temp_dict

# Month-Day-Occurence
def get_frequencies(vanx_df):
    cust_mdo_df = vanx_df.groupby(['Customer_ID', 'Site_Use_ID', 'Month_Day_Occurence']).agg({'Creation_Date': {'Freq_Unique_MDO': 'nunique'}, 'Orig_Sys_Document_Ref': {'Freq_MDO': 'nunique'}}).reset_index()
    cust_mdo_df.columns = cust_mdo_df.columns.droplevel(1)
    cust_mdo_df = cust_mdo_df.rename(columns = {'Orig_Sys_Document_Ref': 'Freq_MDO', 'Creation_Date': 'Freq_Unique_MDO'})
    # cust_mdo_df = pandas.merge(cust_mdo_df, vanx_df[['Month_Day_Occurence', 'All_Month_Day_Occurence']].drop_duplicates(), on='Month_Day_Occurence')
    cust_mdo_df = pandas.merge(cust_mdo_df, vanx_df[['Customer_ID', 'Site_Use_ID', 'Month_Day_Occurence', 'All_Month_Day_Occurence']].drop_duplicates(), on=['Customer_ID', 'Site_Use_ID', 'Month_Day_Occurence'])
    
    return cust_mdo_df

# Day-Occurence
def get_frequencies_do(vanx_df):
    cust_do_df = vanx_df.groupby(['Customer_ID', 'Site_Use_ID', 'Day_Occurence']).agg({'Creation_Date': {'Freq_Unique_DO': 'nunique'}, 'Orig_Sys_Document_Ref': {'Freq_DO': 'nunique'}}).reset_index()
    cust_do_df.columns = cust_do_df.columns.droplevel(1)
    cust_do_df = cust_do_df.rename(columns = {'Orig_Sys_Document_Ref': 'Freq_DO', 'Creation_Date': 'Freq_Unique_DO'})
    cust_do_df = pandas.merge(cust_do_df, vanx_df[['Customer_ID', 'Site_Use_ID', 'Day_Occurence', 'All_Day_Occurence']].drop_duplicates(), on=['Customer_ID', 'Site_Use_ID', 'Day_Occurence'])
    
    return cust_do_df

def calculate_ratio(cust_mdo_df):
    cust_mdo_df['Avg_Unique_MDO_Freq'] = cust_mdo_df['Freq_Unique_MDO']/cust_mdo_df['All_Month_Day_Occurence']
    cust_mdo_df['Avg_MDO_Freq'] = cust_mdo_df['Freq_MDO']/cust_mdo_df['All_Month_Day_Occurence']
    return cust_mdo_df

def calculate_ratio_do(cust_do_df):
    cust_do_df['Avg_Unique_DO_Freq'] = cust_do_df['Freq_Unique_DO']/cust_do_df['All_Day_Occurence']
    cust_do_df['Avg_DO_Freq'] = cust_do_df['Freq_DO']/cust_do_df['All_Day_Occurence']
    return cust_do_df

def generate_mdo_frequency_table(van_id, cur, conn, client_name, bq_db, rftable_logger):
    x_df = get_van_wise_df(van_id, bq_db, client_name)

    start = timeit.default_timer()
    x_df = get_mdo_df(x_df)

    # Oldest Date
    oldest_df = x_df.groupby(['Customer_ID', 'Site_Use_ID']).agg({'Creation_Date' : np.min}).reset_index().rename(columns = {'Creation_Date': 'Join_Date'})

    # Merge
    x_df = pandas.merge(x_df, oldest_df, on=['Customer_ID', 'Site_Use_ID'])

    # All Month Day Occurence
    temp_dict = {}

    # x_df['All_Month_Day_Occurence'] = x_df.apply(lambda row: get_overall_mdo(row['Month_Day_Occurence'], row['Join_Date']), axis=1)
    for i in range(len(x_df)):
        amdo, temp_dict = get_overall_mdo(x_df.get_value(i, 'Month_Day_Occurence'), x_df.get_value(i, 'Join_Date'), temp_dict)
        x_df.set_value(i, 'All_Month_Day_Occurence', amdo)

    cust_mdo_df = get_frequencies(x_df)
    cust_mdo_df = calculate_ratio(cust_mdo_df)
    cust_mdo_df['Van_No'] = van_id

    # Update DB
    try:
        query=''' insert or replace into Freq_MDO ('Customer_ID', 'Site_Use_ID', 'Month_Day_Occurence', 'Freq_MDO', 'Freq_Unique_MDO', 'All_Month_Day_Occurence',  
                'Avg_Unique_MDO_Freq', 'Avg_MDO_Freq', 'Van_No') values (?,?,?,?,?,?,?,?,?) ''' # Check the replace part
        cur.executemany(query, cust_mdo_df.to_records(index=False))
        conn.commit()
    
    except Exception as e:
        rftable_logger.exception(str(e))

    return cust_mdo_df

def generate_do_frequency_table(van_id, cur, conn, client_name, bq_db, rftable_logger):
    x_df = get_van_wise_df(van_id, bq_db, client_name)

    start = timeit.default_timer()
    x_df = get_do_df(x_df)

    # Oldest Date
    oldest_df = x_df.groupby(['Customer_ID', 'Site_Use_ID']).agg({'Creation_Date' : np.min}).reset_index().rename(columns = {'Creation_Date': 'Join_Date'})
    
    # Merge
    x_df = pandas.merge(x_df, oldest_df, on=['Customer_ID', 'Site_Use_ID'])

    # All Month Day Occurence
    temp_dict = {}

    x_df['All_Day_Occurence'] = 0

    for i in range(len(x_df)):
        ado, temp_dict = get_overall_do(x_df.get_value(i, 'Day_Occurence'), str(x_df.get_value(i, 'Customer_ID')), str(x_df.get_value(i, 'Site_Use_ID')), x_df.get_value(i, 'Join_Date'), temp_dict)
        x_df.set_value(i, 'All_Day_Occurence', ado)
                
    cust_do_df = get_frequencies_do(x_df)
    cust_do_df = calculate_ratio_do(cust_do_df)
    cust_do_df['Van_No'] = van_id

    # Update DB
    try:
        query=''' insert or replace into Freq_DO ('Customer_ID', 'Site_Use_ID', 'Day_Occurence', 'Freq_DO', 'Freq_Unique_DO', 'All_Day_Occurence', 
                'Avg_Unique_DO_Freq', 'Avg_DO_Freq', 'Van_No') values (?,?,?,?,?,?,?,?,?) ''' # Check the replace part
        cur.executemany(query, cust_do_df.to_records(index=False))
        conn.commit()

    except Exception as e:
        rftable_logger.exception(str(e))

    return cust_do_df

def generate_frequency_table(van_id, cur, conn, client_name, bq_db, rftable_logger):
    # Month-Day-Occurrence
    cust_mdo_df = generate_mdo_frequency_table(van_id, cur, conn, client_name, bq_db, rftable_logger)

    # Day-Occurrence
    cust_do_df = generate_do_frequency_table(van_id, cur, conn, client_name, bq_db, rftable_logger)

    return cust_mdo_df, cust_do_df

def generate_for_all_clients(client_name, dbcl, bq_db, dataset_ref, rftable_logger, setting_paths):
    json_resps = db_functions.get_client_db_info('all', dbcl)

    flag = 0

    for resp in json_resps:
        client_name = resp[0]

        conn, cur = db_functions.get_database(setting_paths['sqlite_db']+'databases/'+client_name+'/'+client_name+'.sqlite')

        try:
            rfmrsm = RFMRSM()
            avg_lrfm_df, chk1 = rfmrsm.calculate_default_rfm(cur, conn, bq_db, client_name, rftable_logger, setting_paths)
            try:
                avg_lrsm_df, chk2 = rfmrsm.calculate_default_rsm(cur, conn, bq_db, client_name, rftable_logger)
            except:
                pass

            active_vans = db_functions.get_all_active_vans(cur)

            for van in active_vans:
                if is_van_route_freq_possible(bq_db, van, client_name):
                    freq_mdo_df, freq_do_df = generate_frequency_table(van, cur, conn, client_name, bq_db, rftable_logger)
                    # Generate Routes for All Active Vans
                    chk = route_generator.main(avg_lrfm_df, freq_mdo_df, freq_do_df, van, resp, cur, conn, client_name, bq_db, dataset_ref, rftable_logger, setting_paths)
                    rftable_logger.info(chk)
                else:
                    flag = 1
                    rftable_logger.info('Frequency & Route Generation Failed for Van: '+str(van)+' due to insufficient data.')

        except Exception as err:
            rftable_logger.exception(str(err))
            flag = 1
            continue

    if flag:
        return {'success': True, 'message': 'Partial Success, Check logs!'}

    return {'success': True, 'message': 'Success'}

def main(client_name, van, dbcl, bq_db, dataset_ref, rftable_logger, setting_paths):
    flag = 0

    if client_name != 'all':
        tup_resp = db_functions.get_client_db_info(client_name, dbcl)

        if tup_resp:
        
            conn, cur = db_functions.get_database(setting_paths['sqlite_db']+'databases/'+client_name+'/'+client_name+'.sqlite')

            try:
                start = timeit.default_timer()
                rfmrsm = RFMRSM()
                avg_lrfm_df, chk1 = rfmrsm.calculate_default_rfm(cur, conn, bq_db, client_name, rftable_logger, setting_paths)
                avg_lrsm_df, chk2 = rfmrsm.calculate_default_rsm(cur, conn, bq_db, client_name, rftable_logger, setting_paths)

                active_vans = db_functions.get_all_active_vans(cur)

                if van != 'all':
                    if is_van_route_freq_possible(bq_db, van, client_name):
                        if van in active_vans:
                            freq_mdo_df, freq_do_df = generate_frequency_table(van, cur, conn, client_name, bq_db, rftable_logger)
                        else:
                            return {'success': False, 'message': 'Either Van is Inactive or Van does not exist.'}

                        chk = route_generator.main(avg_lrfm_df, freq_mdo_df, freq_do_df, van, tup_resp, cur, conn, client_name, bq_db, dataset_ref, rftable_logger, setting_paths)
                        rftable_logger.info(chk)
                    else:
                        flag = 1
                        rftable_logger.info('Frequency & Route Generation Failed for Van: '+str(van)+' due to insufficient data.')
                else:
                    for van in active_vans:
                        if is_van_route_freq_possible(bq_db, van, client_name):
                            freq_mdo_df, freq_do_df = generate_frequency_table(van, cur, conn, client_name, bq_db, rftable_logger)

                            # Generate Routes for All Active Vans
                            chk = route_generator.main(avg_lrfm_df, freq_mdo_df, freq_do_df, van, tup_resp, cur, conn, client_name, bq_db, dataset_ref, rftable_logger, setting_paths)
                            rftable_logger.info(chk)
                        else:
                            flag = 1
                            rftable_logger.info('Frequency & Route Generation Failed for Van: '+str(van)+' due to insufficient data.')

            except Exception as err:
                rftable_logger.exception(str(err))
                return {'success': False, 'message': str(err)}

            if chk1 == 'success' and chk2 == 'success' and not flag:
                return {'success': True, 'message': 'Success'}

            elif chk1 == 'success' and chk2 == 'success' and flag:
                return {'success': False, 'message': 'Partial Success, Check Logs!'}

            else:
                return {'success': False, 'message': 'Error in calculating RFM / Product_RFM / Freq Table / Routes, Check Logs!'}

        else:
            return {'success': False, 'message': 'No Such Client: '+str(client_name)}
    
    else:
        resp = generate_for_all_clients(client_name, dbcl, bq_db, dataset_ref, rftable_logger, setting_paths)
        return resp