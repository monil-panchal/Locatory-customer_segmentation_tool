from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query

from app.log import Log
from .rfm import RFM
from .rfm_parameters_validation import RFMParametersValidation

router = APIRouter()

rfm_logger = Log.get_instance().root_logger


@router.post("/rfm_segmentation_with_saved_data/", response_model=bool)
async def rfm_segmentation_with_saved_data(document_id: str = Query(None, min_length=20, max_length=30)):
    rfm_logger.info(
        "Request to perform RFM Segmentation with saved parameters, document_id: {}".format(document_id))

    # Perform RFM Segmentation
    rfm_obj = RFM(rfm_parameters.dict())
    rfm_data_doc_id = rfm_obj.perform_rfm_segmentation(rfm_logger)

    return True


@router.post("/rfm_segmentation_with_parameters", response_model=bool)
async def rfm_segmentation_with_parameters(rfm_parameters: RFMParametersValidation):
    rfm_logger.info(
        "Request to perform RFM Segmentation with parameters: {}".format(rfm_parameters.dict()))

    # Perform RFM Segmentation
    rfm_obj = RFM(rfm_parameters.dict())
    rfm_data_doc_id = rfm_obj.perform_rfm_segmentation(rfm_logger)

    return True
