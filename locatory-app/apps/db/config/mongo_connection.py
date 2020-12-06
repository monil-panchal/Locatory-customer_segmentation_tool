import os

from pymongo import MongoClient
from urllib.parse import quote_plus

class PyMongo:

    def __init__(self):
        self.dbname = os.environ.get('DB_NAME', "locatorydb")
        self.username = os.environ.get('DB_USERNAME', "admin")
        self.password = os.environ.get('DB_PASSWORD', "locatorydb@123")
        self.url = os.environ.get('DB_URL', "129.173.67.205")
        self.client = None

    def get_db_connection(self):
        self.client = MongoClient(
            f"mongodb://{quote_plus(self.username)}:{quote_plus(self.password)}@{self.url}:27017/{self.dbname}?authSource=admin")
        return self.client.get_database()

    def close_db_connection(self):
        if self.client is not None:
            self.client.close()

