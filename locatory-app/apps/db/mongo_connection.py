from pymongo import MongoClient

class PyMongo:

    def __init__(self, dbname='locatorydb', password='tzNtakzxBnWmq22'):
        self.dbname = dbname
        self.password = password

    def get_db_connection(self):
        client = MongoClient(
            f"mongodb+srv://admin:{self.password}@cluster0.slfeg.mongodb.net/{self.dbname}?retryWrites=true&w=majority")
        return client.get_database()
