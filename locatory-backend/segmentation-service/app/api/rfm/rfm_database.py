import pandas as pd

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo import IndexModel, ASCENDING, DESCENDING

from app.configs import cfg


class RFMDatabase:
    __instance__ = None
    _client = None
    _db = None

    def __init__(self):
        """ Constructor.
        """
        if RFMDatabase.__instance__ is None:
            RFMDatabase.__instance__ = self
            self._client = MongoClient(
                host=self.get_database_url(), port=self.get_database_port(),
                username=self.get_database_username(), password=self.get_database_password())
            self._db = self._client[self.get_database_name()]
        else:
            raise Exception(
                "You cannot create another Singleton RFMDatabase class")

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
        """
        if not RFMDatabase.__instance__:
            RFMDatabase()
        return RFMDatabase.__instance__

    def get_database_url(self):
        return cfg.MONGODB_URL

    def get_database_port(self):
        return cfg.MONGODB_PORT

    def get_database_name(self):
        return cfg.MONGODB_DATABASE_NAME

    def get_database_username(self):
        return cfg.MONGODB_USERNAME

    def get_database_password(self):
        return cfg.MONGODB_PASSWORD

    def run_query(self, query):
        data = query
        return data

    def add_rfm_date_match_query(self, and_query_list, start_date, end_date):
        date_query = {"order_date": {'$gte': start_date, '$lt': end_date}}
        and_query_list.append(date_query)

        return and_query_list

    def add_rfm_demography_match_query(self, and_query_list, demography_data):
        if demography_data:
            for k, v in demography_data.items():
                if v:
                    if k == "gender":
                        and_query_list.append({"customer."+k: {"$in": v}})

                    elif k in ["age_range", "income_range"]:
                        demo_data = {
                            "customer."+k.replace("_range", ""): {'$gte': v[0], '$lte': v[1]}}
                        and_query_list.append(demo_data)

        return and_query_list

    def add_rfm_geography_match_query(self, and_query_list, geography_data):
        if geography_data:
            for k, v in geography_data.items():
                if v:
                    and_query_list.append(
                        {"customer.address.customer_"+k: {"$in": v}})

        return and_query_list

    def generate_rfm_match_query(self, start_date, end_date, rfm_parameters):
        and_query_list = []

        and_query_list = self.add_rfm_date_match_query(
            and_query_list, start_date, end_date)
        and_query_list = self.add_rfm_demography_match_query(
            and_query_list, rfm_parameters.get("demography"))
        and_query_list = self.add_rfm_geography_match_query(
            and_query_list, rfm_parameters.get("geography"))

        match_query = {"$and": and_query_list}

        return match_query

    def rfm_query_builder(self, start_date, end_date, rfm_parameters):
        ''' Sample query:
        db.getCollection('Orders').aggregate([
                                    { $match: { }},
                                    { $group: {_id: "$customer.customer_id", M: {$sum: "$payment_value"}, F: {$sum: 1},
                                    Latest_Order_Date: {$max: "$order_date"}, First_Order_Date: {$min: "$order_date"} }}
                                    ])
        '''
        aggregation_pipeline = []
        match_query = self.generate_rfm_match_query(
            start_date, end_date, rfm_parameters)
        match_stage = {"$match": match_query}
        aggregation_pipeline.append(match_stage)
        group_stage = {"$group": {"_id": "$customer.customer_id", "M": {"$sum": "$payment_value"}, "F": {"$sum": 1},
                                  "Latest_Order_Date": {"$max": "$order_date"}, "First_Order_Date": {"$min": "$order_date"}}}
        aggregation_pipeline.append(group_stage)

        return aggregation_pipeline

    def get_rfm_dataframe(self, start_date, end_date, rfm_parameters):
        aggregation_pipeline = self.rfm_query_builder(
            start_date, end_date, rfm_parameters)

        # Orders collection
        data = self._db['Orders'].aggregate(aggregation_pipeline)
        df = pd.DataFrame(list(data))

        return df
