from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, HTTPException

from app.log import Log
from .rfm import RFM
from .parameters_validation import DocumentIDValidation, RFMParametersValidation
from .rfm_database import RFMDatabase

router = APIRouter()

rfm_logger = Log.get_instance().root_logger


@router.post("/rfm_segmentation_with_saved_data/", response_model=str)
async def rfm_segmentation_with_saved_data(document_id: DocumentIDValidation):
    rfm_logger.info(
        "Request to perform RFM Segmentation with saved parameters: {}".format(document_id))

    # Get rfm parameters
    document_id = document_id.dict().get("document_id")
    rfm_parameters = RFMDatabase.get_instance().get_segmentation_parameters(document_id)
    if not rfm_parameters:
        raise HTTPException(status_code=404, detail="Document not found")

    # Perform RFM Segmentation
    rfm_obj = RFM(rfm_parameters, document_id)
    try:
        rfm_df, start_date, end_date = rfm_obj.perform_rfm_segmentation(
            rfm_logger)
        if rfm_df.empty:
            raise HTTPException(status_code=404)

        saved_document_id = RFMDatabase.get_instance().save_rfm_segments_data(
            rfm_df, document_id, rfm_parameters, start_date, end_date)

    except HTTPException:
        raise HTTPException(status_code=404, detail="No order data found")

    except Exception as err:
        rfm_logger.exception("Unexpected Error: {}".format(err))
        raise HTTPException(
            status_code=500, detail="Server encountered an unexpected error")

    return str(saved_document_id)


@router.post("/rfm_segmentation_with_parameters", response_model=list)
async def rfm_segmentation_with_parameters(rfm_parameters: RFMParametersValidation):
    rfm_logger.info(
        "Request to perform RFM Segmentation with parameters: {}".format(rfm_parameters.dict()))

    # Perform RFM Segmentation
    rfm_obj = RFM(rfm_parameters.dict(), None)
    try:
        rfm_df, start_date, end_date = rfm_obj.perform_rfm_segmentation(
            rfm_logger)
    except Exception as err:
        rfm_logger.exception("Unexpected Error: {}".format(err))
        raise HTTPException(
            status_code=500, detail="Server encountered an unexpected error")

    return rfm_df.to_dict('records')
