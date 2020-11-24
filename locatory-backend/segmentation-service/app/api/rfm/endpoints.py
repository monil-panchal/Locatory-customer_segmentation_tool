from fastapi import APIRouter, HTTPException, status

from app.log import Log

router = APIRouter()

rfm_logger = Log.get_instance().root_logger

@router.post("/perform_rfm_segmentation/", response_model=bool)
async def perform_rfm_segmentation():
    rfm_logger.info("Request to perform RFM Segmentation")
    return True
