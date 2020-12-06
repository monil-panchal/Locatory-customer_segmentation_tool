import os

from pymongo import MongoClient
from urllib.parse import quote_plus

dbname = os.environ.get('DB_NAME', "locatorydb")
password = os.environ.get('DB_PASSWORD', "locatorydb@123")
url = os.environ.get('DB_URL', "129.173.67.205")

class PyMongo:

    def __init__(self, dbname=dbname, password=password):
        self.dbname = dbname
        self.password = password
        self.client = None

    def get_db_connection(self):
        self.client = MongoClient(
            f"mongodb://{quote_plus('admin')}:{quote_plus(self.password)}@{url}:27017/{self.dbname}?authSource=admin")
        return self.client.get_database()

    def close_db_connection(self):
        if self.client is not None:
            self.client.close()

