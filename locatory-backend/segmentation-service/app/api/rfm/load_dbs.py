import sqlite3
from sqlite3 import Error
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from google.cloud import bigquery

def get_client_list_db(setting_paths):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(setting_paths['sqlite_db']+"databases/client_list_db.sqlite")
        return conn

    except Error as e:
        print str(e)
        return None

def get_bigquery_db(setting_paths):
    """ create a database connection to Bigquery Database/Dataset """
    try:
        client = bigquery.Client.from_service_account_json(setting_paths['required_files']+'required_files/RouteRecommendation-API-530b2c589319.json')
        dataset_ref = client.dataset('route_recommendation_data')
        return client, dataset_ref

    except Error as e:
        print str(e)
        return None

def get_mongodb_database(setting_paths):
    try:
        client = MongoClient(host="localhost", port=27017)
        db = client['salesworx_insights']
        return db

    except Error as e:
        print str(e)
        return None