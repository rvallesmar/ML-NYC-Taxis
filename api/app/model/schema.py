from pydantic import BaseModel, Field, root_validator
from typing import Optional, Dict, List
from datetime import datetime


class FareDurationRequest(BaseModel):
    passenger_count: int = Field(..., ge=1, le=4, description="Number of passengers")
    trip_distance: float = Field(..., gt=0, description="Trip distance in miles")
    pickup_datetime: Optional[str] = Field(None, description="Pickup datetime in format YYYY-MM-DD HH:MM:SS")
    
    @root_validator
    def set_current_datetime(cls, values):
        """Set the current datetime if not provided"""
        if values.get("pickup_datetime") is None:
            values["pickup_datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return values


class FareDurationResponse(BaseModel):
    success: bool
    fare_amount: Optional[float] = None
    trip_duration: Optional[float] = None


class DemandRequest(BaseModel):
    region_id: int = Field(..., description="Region ID (grid cell)")
    date_hour: Optional[str] = Field(None, description="Date and hour in format YYYY-MM-DD HH:MM:SS")
    
    @root_validator
    def set_current_datetime(cls, values):
        """Set the current datetime if not provided"""
        if values.get("date_hour") is None:
            values["date_hour"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return values


class DemandResponse(BaseModel):
    success: bool
    demand: Optional[int] = None