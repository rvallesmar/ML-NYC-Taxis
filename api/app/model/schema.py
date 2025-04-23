from pydantic import BaseModel, Field, root_validator
from typing import Optional, Dict, List


class FareDurationRequest(BaseModel):
    pickup_longitude: float = Field(..., description="Pickup longitude")
    pickup_latitude: float = Field(..., description="Pickup latitude")
    dropoff_longitude: float = Field(..., description="Dropoff longitude")
    dropoff_latitude: float = Field(..., description="Dropoff latitude")
    passenger_count: int = Field(..., ge=1, le=9, description="Number of passengers")
    pickup_datetime: str = Field(..., description="Pickup datetime in format YYYY-MM-DD HH:MM:SS")
    distance: Optional[float] = Field(None, description="Trip distance in miles (optional)")


class FareDurationResponse(BaseModel):
    success: bool
    fare_amount: Optional[float] = None
    trip_duration: Optional[float] = None
    fare_score: Optional[float] = None
    duration_score: Optional[float] = None


class DemandRequest(BaseModel):
    region_id: int = Field(..., description="Region ID (grid cell)")
    date_hour: str = Field(..., description="Date and hour in format YYYY-MM-DD HH:MM:SS")


class DemandResponse(BaseModel):
    success: bool
    demand: Optional[int] = None
    demand_score: Optional[float] = None


class BatchFareDurationRequest(BaseModel):
    requests: List[FareDurationRequest] 