from apps.config.constants import RFM_API_CREDENTIALS, CURRENT_ENV
from apps.db.dao.segmentation_params_dao import SegmentationParameters
import requests
import json
import timeit
from app import server

class RFM:

    @staticmethod
    def get_api_token():
        auth_data = {"username": RFM_API_CREDENTIALS[CURRENT_ENV].get('username'), "password": RFM_API_CREDENTIALS[CURRENT_ENV].get('password')}
        auth_token = None
        try:
            response = requests.post(f"{RFM_API_CREDENTIALS[CURRENT_ENV].get('host')}token", data=auth_data)
            auth_token = response.json()
            server.logger.into(f"get api auth token: {auth_token}")
        except Exception as e:
            server.logger.error(f"Error in get api auth token: {str(e)}")
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
            server.logger.info(f"create rfm seg api call=> header:{header}, data:{data}, startTime: {start}")
            server.logger.info(f"create RFM API endpoint: {RFM_API_CREDENTIALS[CURRENT_ENV].get('host')}rfm/rfm_segmentation_with_saved_data/")
            response = requests.post(f"{RFM_API_CREDENTIALS[CURRENT_ENV].get('host')}rfm/rfm_segmentation_with_saved_data/", data=json.dumps(data),
                                 headers=header)
            server.logger.info(f"create RFM api response: {response}")
            if response is not None and response.status_code == 200:
                server.logger.info(f"create RFM api json response: {response.json()}")
                success = True
            server.logger.info(f"create rfm seg api call=> header:{header}, data:{data}, startTime: {timeit.default_timer() - start}")
        except Exception as e:
            server.logger.info(f"error in create rfm seg api call=>{str(e)}")
            print(str(e))
        return success