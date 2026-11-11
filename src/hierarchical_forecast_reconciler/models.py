from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator
import numpy as np

class ReconciliationRequest(BaseModel):
    """Schema for incoming forecast reconciliation tasks."""
    forecasts: List[List[float]] = Field(..., description="Base forecasts matrix (n_series x n_time)")
    summation_matrix: List[List[float]] = Field(..., description="S-matrix defining hierarchy")
    method: Literal["ols", "wls", "mint_sample", "mint_shrink"] = "mint_shrink"
    
    @field_validator("forecasts", "summation_matrix")
    @classmethod
    def validate_dimensions(cls, v):
        if not v or not v[0]:
            raise ValueError("Matrix cannot be empty")
        return v

class ReconciliationResponse(BaseModel):
    """Schema for reconciled output."""
    reconciled_forecasts: List[List[float]]
    status: str = "success"
    metadata: dict = {}