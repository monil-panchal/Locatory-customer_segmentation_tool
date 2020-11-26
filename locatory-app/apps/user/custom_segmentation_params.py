from apps.db.mongo_connection import PyMongo
import pandas as pd
import numpy as np

class SegmentationParameters():

    def __init__(self):
        pass

    def fetch_all_params(self):
        print("fetching custom seg params from mongodb")
        pymongoObj = PyMongo()
        db = pymongoObj.get_db_connection()
        custom_params = []
        cursor = db.SegmentationParameters.find({}, {'_id':0})
        for item in cursor:
            custom_params.append(item)
        pymongoObj.close_db_connection()
        return custom_params

    def total_count(self):
        print("fetching custom seg params from mongodb")
        pymongoObj = PyMongo()
        db = pymongoObj.get_db_connection()
        count = db.SegmentationParameters.count({})
        pymongoObj.close_db_connection()
        return count

    def insert_custom_mapping(self, custom_mapping_dict):

        insert_dict = {}
        # mandatory params
        if custom_mapping_dict.get('input_segments') is not None and custom_mapping_dict.get('input_segments') >=3 and custom_mapping_dict.get('input_segments') <=10 :
            insert_dict['n_segments'] = custom_mapping_dict.pop('input_segments')
        else:
            return False
        if custom_mapping_dict.get('input_data') is not None and custom_mapping_dict.get('input_data') >=1 and custom_mapping_dict.get('input_data') <=24 :
            insert_dict['data_period'] = custom_mapping_dict.pop('input_data')
        else:
            return False
        if custom_mapping_dict.get('custom_params_title') is not None:
            insert_dict['title'] = custom_mapping_dict.pop('custom_params_title')
        else:
            return False

        if custom_mapping_dict.get('segment-segregator_modal') is not None:
            insert_dict['segment_separators'] = custom_mapping_dict.pop('segment-segregator_modal')

        if custom_mapping_dict.get('segmentation_algorithm_modal') is not None:
            insert_dict['segmentation_algorithm'] = custom_mapping_dict.pop('segmentation_algorithm_modal')

        # demography params
        insert_dict['demography'] = {}
        if custom_mapping_dict.get('gender_checkbox_modal') is not None:
            insert_dict['demography']['genders'] = custom_mapping_dict.pop('gender_checkbox_modal')
        if custom_mapping_dict.get('age-range-slider_modal') is not None:
            insert_dict['demography']['age_range'] = custom_mapping_dict.pop('age-range-slider_modal')
        if custom_mapping_dict.get('income-range-slider_modal') is not None:
            insert_dict['demography']['income_range'] = custom_mapping_dict.pop('income-range-slider_modal')

        # geography params
        insert_dict['geography'] = {}
        if custom_mapping_dict.get('country_checkbox_modal') is not None:
            insert_dict['geography']['country'] = custom_mapping_dict.pop('country_checkbox_modal')
        if custom_mapping_dict.get('state_dropdown_modal') is not None:
            insert_dict['geography']['state'] = custom_mapping_dict.pop('state_dropdown_modal')
        if custom_mapping_dict.get('city_dropdown_modal') is not None:
            insert_dict['geography']['city'] = custom_mapping_dict.pop('city_dropdown_modal')

        try:
            print("inserting custom seg params to mongodb")
            pymongoObj = PyMongo()
            db = pymongoObj.get_db_connection()
            db.SegmentationParameters.insert_one(insert_dict)
            pymongoObj.close_db_connection()
        except Exception as e:
            print(e)
            return False
        print(insert_dict)
        return True

    def is_title_exist(self, title):
        pymongoObj = PyMongo()
        db = pymongoObj.get_db_connection()
        count = db.SegmentationParameters.count({ "title": f"{title.strip()}" })
        if count>0:
            return True
        pymongoObj.close_db_connection()
        return False
