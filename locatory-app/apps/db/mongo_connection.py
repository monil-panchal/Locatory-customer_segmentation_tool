from pymongo import MongoClient
from urllib.parse import quote_plus

class PyMongo:

    def __init__(self, dbname='locatorydb', password='locatorydb@123'):
        self.dbname = dbname
        self.password = password
        self.client = None

    def get_db_connection(self):
        self.client = MongoClient(
            f"mongodb://{quote_plus('admin')}:{quote_plus(self.password)}@129.173.67.205:27017/{self.dbname}?authSource=admin")
        return self.client.get_database()

    def close_db_connection(self):
        if self.client is not None:
            try:
                self.client.close()
            except Exception as e:
                print(e)

