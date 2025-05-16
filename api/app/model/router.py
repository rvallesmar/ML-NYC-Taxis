from app import db
from app.auth.jwt import get_current_user
from app.model.schema import (DemandRequest,
                              DemandResponse, FareDurationRequest,
                              FareDurationResponse)
from app.model.services import predict_demand, predict_fare_duration
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(tags=["Model"], prefix="/model")


@router.post("/predict/fare_duration", response_model=FareDurationResponse)
async def predict_fare_duration_endpoint(
    request: FareDurationRequest,
    current_user=Depends(get_current_user)
):
    """
    Predict fare amount and trip duration for a taxi ride.
    
    This endpoint takes the trip distance in miles, number of passengers,
    and pickup datetime, and returns predicted fare and duration.
    """
    # Initialize response with success=False as default
    response = {"success": False}
    
    try:
        # Extract data from the request using Pydantic's dict() method
        # This validates the input data against the schema
        data = request.dict()
        
        # Call the predict_fare_duration service which handles Redis communication
        # This sends the job to the model service and waits for the result
        fare_amount, trip_duration = await predict_fare_duration(data)
        
        # Update response with prediction results
        response["success"] = True
        response["fare_amount"] = fare_amount
        response["trip_duration"] = trip_duration
        
    except TimeoutError as e:
        # Handle timeout errors specifically
        print(f"Prediction timeout: {e}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Prediction timed out. Please try again later."
        )
    except Exception as e:
        # Handle other errors that might occur
        print(f"Error predicting fare and duration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process request: {str(e)}"
        )
    
    # Return the response using the FareDurationResponse Pydantic model
    # This validates the output format
    return FareDurationResponse(**response)


@router.post("/predict/demand", response_model=DemandResponse)
async def predict_demand_endpoint(
    request: DemandRequest,
    current_user=Depends(get_current_user)
):
    """
    Predict taxi demand for a specific region and time.
    
    This endpoint takes a region ID and date/hour and returns the predicted number
    of pickup requests for that region and time.
    """
    # Initialize response with success=False as default
    response = {"success": False}
    
    try:
        # Extract data from the request using Pydantic's dict() method
        # This validates the input data against the schema
        data = request.dict()
        
        # Call the predict_demand service which handles Redis communication
        # This sends the job to the model service and waits for the result
        demand = await predict_demand(data)
        
        # Update response with prediction results
        response["success"] = True
        response["demand"] = demand
        
    except TimeoutError as e:
        # Handle timeout errors specifically
        print(f"Prediction timeout: {e}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Prediction timed out. Please try again later."
        )
    except Exception as e:
        # Handle other errors that might occur
        print(f"Error predicting demand: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process request: {str(e)}"
        )
    
    # Return the response using the DemandResponse Pydantic model
    # This validates the output format
    return DemandResponse(**response)