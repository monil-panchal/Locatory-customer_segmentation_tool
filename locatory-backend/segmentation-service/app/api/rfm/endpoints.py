from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query

from app.log import Log
from .rfm_parameters import RFMParameters

router = APIRouter()

rfm_logger = Log.get_instance().root_logger

@router.post("/rfm_segmentation_with_saved_data/", response_model=bool)
async def rfm_segmentation_with_saved_data(document_id: str = Query(None, min_length=20, max_length=30)):
    rfm_logger.info("Request to perform RFM Segmentation")
    return True

@router.post("/rfm_segmentation_with_parameters", response_model=bool)
async def rfm_segmentation_with_parameters(rfm_parameters: RFMParameters):
    rfm_logger.info("Request to perform RFM Segmentation")
    return True
