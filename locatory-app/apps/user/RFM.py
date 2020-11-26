from apps.config.constants import RFM_API_CREDENTIALS, CURRENT_ENV
from apps.user.custom_segmentation_params import SegmentationParameters
import requests
import json
import timeit

class RFM:

    @staticmethod
    def get_api_token():
        auth_data = {"username": RFM_API_CREDENTIALS[CURRENT_ENV].get('username'), "password": RFM_API_CREDENTIALS[CURRENT_ENV].get('password')}
        auth_token = None
        try:
            response = requests.post(f"{RFM_API_CREDENTIALS[CURRENT_ENV].get('host')}token", data=auth_data)
            auth_token = response.json()
            print(auth_token)
        except Exception as e:
            print(str(e))
        return auth_token

    def create_rfm_segmentation(self, seg_params_mongo_id):
        sp = SegmentationParameters()
        success = False
        if not sp.is_attribute_exist('_id', seg_params_mongo_id):
            # check if mongoid exist
            return False
        auth_token = RFM.get_api_token()
        try:
            header = {'content-type': 'application/json',
                      'Authorization': 'Bearer ' + auth_token['access_token']}
            data = {"document_id": seg_params_mongo_id}
            start = timeit.default_timer()
            response = requests.post(f"{RFM_API_CREDENTIALS[CURRENT_ENV].get('host')}rfm/rfm_segmentation_with_saved_data", data=json.dumps(data),
                                 headers=header)
            print(response)
            if response is not None and response.status_code == 200:
                print(response.json())
                success = True
            print(timeit.default_timer() - start)
        except Exception as e:
            print(str(e))
        return success