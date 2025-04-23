import datetime
from typing import Optional

import folium
import pandas as pd
import requests
import streamlit as st
from app.settings import API_BASE_URL, DEFAULT_MAP_LOCATION, DEFAULT_ZOOM, PAGE_ICON, PAGE_TITLE
from streamlit_folium import folium_static


def login(username: str, password: str) -> Optional[str]:
    """This function calls the login endpoint of the API to authenticate the user
    and get a token.

    Args:
        username (str): email of the user
        password (str): password of the user

    Returns:
        Optional[str]: token if login is successful, None otherwise
    """
    # TODO: Implement the login function
    # 1. Construct the API endpoint URL
    # 2. Set up the request headers
    # 3. Prepare the data payload
    # 4. Send the API request
    # 5. Check if the response is successful
    # 6. Extract the token from the response
    # 7. Return the token if successful, None otherwise
    
    url = f"{API_BASE_URL}/login"
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
    
    return None


def predict_fare_duration(token: str, data: dict) -> requests.Response:
    """This function calls the predict_fare_duration endpoint of the API.

    Args:
        token (str): token to authenticate the user
        data (dict): prediction data including coordinates, passengers, etc.

    Returns:
        requests.Response: response from the API
    """
    # TODO: Implement the predict_fare_duration function
    # 1. Construct the API endpoint URL
    # 2. Set up the request headers with the token
    # 3. Send the API request
    # 4. Return the response
    
    url = f"{API_BASE_URL}/model/predict/fare_duration"
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response
    except Exception as e:
        st.error(f"Prediction failed: {str(e)}")
        return None


def predict_demand(token: str, data: dict) -> requests.Response:
    """This function calls the predict_demand endpoint of the API.

    Args:
        token (str): token to authenticate the user
        data (dict): prediction data including region_id and date_hour

    Returns:
        requests.Response: response from the API
    """
    # TODO: Implement the predict_demand function
    # 1. Construct the API endpoint URL
    # 2. Set up the request headers with the token
    # 3. Send the API request
    # 4. Return the response
    
    url = f"{API_BASE_URL}/model/predict/demand"
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response
    except Exception as e:
        st.error(f"Demand prediction failed: {str(e)}")
        return None


def send_feedback(token: str, feedback: str, prediction_type: str, prediction_data: dict) -> requests.Response:
    """This function calls the feedback endpoint of the API to send feedback about
    the prediction.

    Args:
        token (str): token to authenticate the user
        feedback (str): feedback text
        prediction_type (str): "fare_duration" or "demand"
        prediction_data (dict): the original prediction data

    Returns:
        requests.Response: response from the API
    """
    # TODO: Implement the send_feedback function
    # 1. Create a dictionary with the feedback data
    # 2. Add the token to the headers
    # 3. Make a POST request to the feedback endpoint
    # 4. Return the response
    
    url = f"{API_BASE_URL}/feedback"
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    feedback_data = {
        "feedback": feedback,
        "prediction_type": prediction_type,
        "prediction_data": prediction_data
    }
    
    try:
        response = requests.post(url, headers=headers, json=feedback_data)
        return response
    except Exception as e:
        st.error(f"Sending feedback failed: {str(e)}")
        return None


# User interface
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)
st.markdown(
    f"<h1 style='text-align: center; color: #FFDD00;'>{PAGE_TITLE}</h1>",
    unsafe_allow_html=True,
)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Fare & Duration Prediction", "Demand Prediction"])

# Login form
if "token" not in st.session_state:
    st.markdown("## Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        token = login(username, password)
        if token:
            st.session_state.token = token
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Login failed. Please check your credentials.")
else:
    st.success("You are logged in!")
    token = st.session_state.token

    if page == "Fare & Duration Prediction":
        st.markdown("## Fare & Duration Prediction")
        
        # Input form for fare/duration prediction
        col1, col2 = st.columns(2)
        
        with col1:
            pickup_longitude = st.number_input("Pickup Longitude", value=-73.98)
            pickup_latitude = st.number_input("Pickup Latitude", value=40.73)
            passenger_count = st.slider("Passenger Count", min_value=1, max_value=9, value=1)
        
        with col2:
            dropoff_longitude = st.number_input("Dropoff Longitude", value=-73.96)
            dropoff_latitude = st.number_input("Dropoff Latitude", value=40.78)
            pickup_datetime = st.date_input("Pickup Date") 
            pickup_time = st.time_input("Pickup Time")
        
        # Combine date and time
        pickup_datetime_str = f"{pickup_datetime} {pickup_time}"
        
        # Calculate distance (This would be more accurate with proper geo-calculations)
        # TODO: Implement haversine distance calculation
        
        # Submit button
        if st.button("Predict Fare & Duration"):
            prediction_data = {
                "pickup_longitude": pickup_longitude,
                "pickup_latitude": pickup_latitude,
                "dropoff_longitude": dropoff_longitude,
                "dropoff_latitude": dropoff_latitude,
                "passenger_count": passenger_count,
                "pickup_datetime": pickup_datetime_str
            }
            
            response = predict_fare_duration(token, prediction_data)
            
            if response and response.status_code == 200:
                result = response.json()
                st.session_state.last_prediction = result
                st.session_state.last_prediction_data = prediction_data
                st.session_state.last_prediction_type = "fare_duration"
                
                # Display results
                st.success("Prediction successful!")
                
                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    st.metric(
                        label="Estimated Fare", 
                        value=f"${result.get('fare_amount', 0):.2f}",
                        delta=None
                    )
                    st.caption(f"Confidence: {result.get('fare_score', 0):.2%}")
                
                with res_col2:
                    minutes = result.get('trip_duration', 0) / 60
                    st.metric(
                        label="Estimated Duration", 
                        value=f"{int(minutes // 60)}h {int(minutes % 60)}m",
                        delta=None
                    )
                    st.caption(f"Confidence: {result.get('duration_score', 0):.2%}")
                
                # Display map
                st.subheader("Route Map")
                m = folium.Map(location=DEFAULT_MAP_LOCATION, zoom_start=DEFAULT_ZOOM)
                
                # Add markers for pickup and dropoff
                folium.Marker(
                    [pickup_latitude, pickup_longitude],
                    popup="Pickup Location",
                    icon=folium.Icon(color="green", icon="play"),
                ).add_to(m)
                
                folium.Marker(
                    [dropoff_latitude, dropoff_longitude],
                    popup="Dropoff Location",
                    icon=folium.Icon(color="red", icon="stop"),
                ).add_to(m)
                
                # Add a line between pickup and dropoff
                folium.PolyLine(
                    locations=[[pickup_latitude, pickup_longitude], 
                               [dropoff_latitude, dropoff_longitude]],
                    color="blue",
                    weight=2,
                    opacity=0.7
                ).add_to(m)
                
                # Display the map
                folium_static(m)
            else:
                if response:
                    st.error(f"Prediction failed: {response.text}")
                else:
                    st.error("Prediction failed. Please try again.")
    
    elif page == "Demand Prediction":
        st.markdown("## Taxi Demand Prediction")
        
        # Input form for demand prediction
        col1, col2 = st.columns(2)
        
        with col1:
            region_id = st.number_input("Region ID", min_value=1, max_value=100, value=1)
        
        with col2:
            prediction_date = st.date_input("Date")
            prediction_hour = st.time_input("Time")
        
        # Combine date and time
        date_hour_str = f"{prediction_date} {prediction_hour}"
        
        # Submit button
        if st.button("Predict Demand"):
            prediction_data = {
                "region_id": region_id,
                "date_hour": date_hour_str
            }
            
            response = predict_demand(token, prediction_data)
            
            if response and response.status_code == 200:
                result = response.json()
                st.session_state.last_prediction = result
                st.session_state.last_prediction_data = prediction_data
                st.session_state.last_prediction_type = "demand"
                
                # Display results
                st.success("Prediction successful!")
                
                st.metric(
                    label=f"Estimated Demand for Region {region_id}", 
                    value=f"{result.get('demand', 0)} pickups",
                    delta=None
                )
                st.caption(f"Confidence: {result.get('demand_score', 0):.2%}")
                
                # TODO: Display heat map of demand across regions
                st.subheader("Demand Heatmap")
                st.info("Heatmap visualization will be implemented here.")
            else:
                if response:
                    st.error(f"Prediction failed: {response.text}")
                else:
                    st.error("Prediction failed. Please try again.")
    
    # Feedback section (shown after a prediction)
    if "last_prediction" in st.session_state:
        st.markdown("## Feedback")
        feedback = st.text_area(
            "If the prediction was wrong, please provide feedback.",
            placeholder="Enter your feedback here..."
        )
        
        if st.button("Send Feedback"):
            if feedback:
                response = send_feedback(
                    token=token,
                    feedback=feedback,
                    prediction_type=st.session_state.last_prediction_type,
                    prediction_data=st.session_state.last_prediction_data
                )
                
                if response and response.status_code in (200, 201):
                    st.success("Thanks for your feedback!")
                else:
                    if response:
                        st.error(f"Error sending feedback: {response.text}")
                    else:
                        st.error("Error sending feedback. Please try again.")
            else:
                st.warning("Please provide feedback before sending.")
    
    # Logout button
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# Footer
st.markdown("<hr style='border:2px solid #FFDD00;'>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #FFDD00;'>NYC Taxi Prediction System</p>",
    unsafe_allow_html=True,
) 