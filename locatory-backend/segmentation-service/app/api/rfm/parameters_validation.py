from typing import Optional, List
from pydantic import BaseModel, validator, Field


class Demography(BaseModel):
    age_range: Optional[List[int]] = Field(
        [],
        min_items=2,
        max_items=2
    )
    gender: Optional[List[str]] = []
    income_range: Optional[List[float]] = Field(
        [],
        min_items=2,
        max_items=2
    )


class Geography(BaseModel):
    country: Optional[List[str]] = []
    state: Optional[List[str]] = []
    city: Optional[List[str]] = []


class RFMParametersValidation(BaseModel):
    n_segments: int
    data_period: int
    segment_separators: Optional[List[float]] = []
    demography: Optional[Demography] = None
    geography: Optional[Geography] = None

    # @validator('n_segments')
    # def passwords_match(cls, v, values):
    #     if 'segment_separators' in values and v != values['segment_separators']:
    #         raise ValueError('segment_separators length must match n_segments')


class DocumentIDValidation(BaseModel):
    document_id: str
