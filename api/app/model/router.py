from app import db
from app.auth.jwt import get_current_user
from app.model.schema import (BatchFareDurationRequest, DemandRequest,
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
    
    This endpoint takes the pickup and dropoff coordinates, number of passengers,
    pickup datetime, and optional distance, and returns predicted fare and duration.
    """
    # Initialize response with success=False as default
    response = {"success": False}
    
    try:
        # Extract data from the request using Pydantic's dict() method
        # This validates the input data against the schema
        data = request.dict()
        
        # Call the predict_fare_duration service which handles Redis communication
        # This sends the job to the model service and waits for the result
        fare_amount, trip_duration, fare_score, duration_score = await predict_fare_duration(data)
        
        # Update response with prediction results
        response["success"] = True
        response["fare_amount"] = fare_amount
        response["trip_duration"] = trip_duration
        response["fare_score"] = fare_score
        response["duration_score"] = duration_score
        
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
        demand, demand_score = await predict_demand(data)
        
        # Update response with prediction results
        response["success"] = True
        response["demand"] = demand
        response["demand_score"] = demand_score
        
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


@router.post("/predict/batch_fare_duration", response_model=list[FareDurationResponse])
async def batch_predict_fare_duration(
    request: BatchFareDurationRequest,
    current_user=Depends(get_current_user)
):
    """
    Batch predict fare amount and trip duration for multiple taxi rides.
    
    This endpoint processes multiple fare/duration prediction requests in a single call.
    """
    # Initialize empty list to store responses
    responses = []
    
    # Process each request in the batch
    for req in request.requests:
        try:
            # Call the single prediction endpoint for each request
            # This reuses the existing endpoint logic
            result = await predict_fare_duration_endpoint(req, current_user)
            responses.append(result)
        except HTTPException as e:
            # Handle exceptions for individual predictions
            # Add a failed response but continue processing other requests
            responses.append(FareDurationResponse(
                success=False,
                fare_amount=None,
                trip_duration=None,
                fare_score=None,
                duration_score=None
            ))
        except Exception as e:
            # Handle unexpected errors
            # Add a failed response but continue processing other requests
            print(f"Unexpected error in batch processing: {e}")
            responses.append(FareDurationResponse(
                success=False,
                fare_amount=None,
                trip_duration=None,
                fare_score=None,
                duration_score=None
            ))
    
    # Return all responses, both successful and failed
    return responses 