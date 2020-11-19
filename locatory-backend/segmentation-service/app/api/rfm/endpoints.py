from fastapi import APIRouter, HTTPException, status


router = APIRouter()


@router.post("/perform_rfm_segmentation/", response_model=bool)
async def perform_rfm_segmentation():
    return True
