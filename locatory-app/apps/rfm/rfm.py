from apps.db.mongo_connection import PyMongo


class RFMData:
    def __init__(self):
        self.db = PyMongo().get_db_connection()
        self.end_dates = []
        self.rfm = []

    def get_all_end_dates(self):
        print('Caling end dates')
        print(self.db.Rfmsample.distinct('end_date'))
        # Get end dates and return a list of all end dates
        return self.db.Rfmsample.distinct('end_date')
