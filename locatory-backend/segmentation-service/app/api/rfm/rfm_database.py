import pandas as pd

from bson.objectid import ObjectId
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

    def insert_one_document(self, doc_data, collection):
        doc_id = collection.insert_one(doc_data).inserted_id
        return doc_id

    def find_one_document(self, query_dict, collection):
        return collection.find_one(query_dict)

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
        or_query_list = []

        if geography_data:
            for k, v in geography_data.items():
                if v:
                    or_query_list.append(
                        {"customer.address.customer_"+k: {"$in": v}})

            if or_query_list:
                and_query_list.append({"$or": or_query_list})

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

    def get_segmentation_parameters(self, document_id):
        query = {"_id": ObjectId(document_id)}
        rfm_parameters = self.find_one_document(
            query, self._db["SegmentationParameters"])

        return rfm_parameters

    def get_label_wise_customer_ids_list(self, df, label_col, cust_id_col, first_label):
        label_data = {first_label: {}}
        unique_scores = sorted(list(set(df[label_col].tolist())))

        for score in unique_scores:
            customer_ids = df.loc[(df[label_col] == score)][
                cust_id_col].tolist()
            label_data[first_label][str(score)] = {
                "customer_ids": list(set(customer_ids))}

        return label_data

    def get_valid_RFM_labels(self, data):
        """
        Compare RFM Labels with n_segments.
        Add labels with empty list if number of
        unique labels are less than n_segments.
        """
        # Max 10 labels because n_segments falls between 3 and 10
        possible_labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        possible_labels = possible_labels[:data.get("segment_count")]

        cur_rfm_labels = list(data.get("RFM").get("segments").keys())
        labels_to_add = set(possible_labels) - set(cur_rfm_labels)

        for label in sorted(list(labels_to_add)):
            data["RFM"]["segments"][label] = {"customer_ids": []}

        return data

    def add_rfm_data_for_rfmsegments_collection(self, data, rfm_df):
        data["R"] = self.get_label_wise_customer_ids_list(
            rfm_df, "R_Score", "_id", "score")
        data["F"] = self.get_label_wise_customer_ids_list(
            rfm_df, "Avg_F_Score", "_id", "score")
        data["M"] = self.get_label_wise_customer_ids_list(
            rfm_df, "Avg_M_Score", "_id", "score")
        data["RFM"] = self.get_label_wise_customer_ids_list(
            rfm_df, "RFM_Label", "_id", "segments")

        data = self.get_valid_RFM_labels(data)

        return data

    def data_for_rfmsegments_collection(self, rfm_df, document_id, rfm_parameters, start_date, end_date):
        data = {"segmentation_parameters_id": document_id, "organization_id": 1, "start_date": start_date,
                "end_date": end_date, "period_month": rfm_parameters.get("data_period"),
                "segment_count": rfm_parameters.get("n_segments")}

        # Add R,F,M, and RFM_Label customer data to data
        data = self.add_rfm_data_for_rfmsegments_collection(data, rfm_df)

        # Add geographic and demographic data
        if rfm_parameters.get("geography"):
            data["location"] = rfm_parameters.get("geography")

        if rfm_parameters.get("demography"):
            data["demography"] = rfm_parameters.get("demography")

        return data

    def overwrite_required(self, doc_data):
        data = self._db['RFMSegments'].find(
            {"segmentation_parameters_id": doc_data.get("segmentation_parameters_id")}).sort(
                [("end_date", -1)]).limit(1)

        if data:
            data = list(data)
            data_dict = data[0]
            search_end_date = data_dict.get("end_date")
            if search_end_date:
                doc_end_date = doc_data.get("end_date")
                doc_year = doc_end_date.date().year
                doc_month = doc_end_date.date().month
                search_year = doc_end_date.date().year
                search_month = doc_end_date.date().month
                if (search_year == doc_year) and (search_month == doc_month):
                    return data_dict.get("_id")

        return None

    def overwrite_document(self, existing_doc_id, doc_data, collection):
        filter = {"_id": ObjectId(existing_doc_id)}
        replaced_doc = collection.replace_one(filter, doc_data)

        if replaced_doc.upserted_id:
            return replaced_doc.upserted_id

        return existing_doc_id

    def save_rfm_segments_data(self, rfm_df, document_id, rfm_parameters, start_date, end_date):
        doc_data = self.data_for_rfmsegments_collection(
            rfm_df, document_id, rfm_parameters, start_date, end_date)

        existing_doc_id = self.overwrite_required(doc_data)
        if not existing_doc_id:
            document_id = self.insert_one_document(
                doc_data, self._db["RFMSegments"])
        else:
            document_id = self.overwrite_document(
                existing_doc_id, doc_data, self._db["RFMSegments"])

        return document_id
