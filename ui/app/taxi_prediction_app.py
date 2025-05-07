import datetime
from typing import Optional

import folium
import pandas as pd
import requests
import streamlit as st
from app.settings import API_BASE_URL, DEFAULT_MAP_LOCATION, DEFAULT_ZOOM, PAGE_ICON, PAGE_TITLE
from streamlit_folium import folium_static
from streamlit_js_eval import streamlit_js_eval
import polyline
import json


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
    
    url = f"{API_BASE_URL}/auth/token"
    
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

def geocode_address(address, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(url)
    result = response.json()
    if result["status"] == "OK":
        location = result["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        return None, None

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
                
        st.title("🚖 Fare & Duration Prediction")

        GOOGLE_MAPS_API_KEY = "AIzaSyCaaee4Cy2UXm86yGaAbsBH5YDjyK4LEGo"

        # Mostrar mapa base de Nueva York
        ny_lat, ny_lng = 40.7128, -74.0060

        with st.form("ruta_form"):
            origen = st.text_input("📍 Origin Address", placeholder="Ej. Times Square, New York")
            destino = st.text_input("🏁 Destination Address", placeholder="Ej. Central Park, New York")
            calcular = st.form_submit_button("Calculate Route")

        if calcular and origen and destino:
            # Llamar a la Directions API
            lat1, lng1 = geocode_address(origen, GOOGLE_MAPS_API_KEY)
            lat2, lng2 = geocode_address(destino, GOOGLE_MAPS_API_KEY)
            directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={lat1},{lng1}&destination={lat2},{lng2}&mode=driving&key={GOOGLE_MAPS_API_KEY}"
            response = requests.get(directions_url)
            data = response.json()

            if data["status"] == "OK":
                route = data["routes"][0]
                puntos = polyline.decode(route["overview_polyline"]["points"])
                # Sumar distancias y duraciones de todos los legs
                distancia_total_m = 0
                duracion_total_s = 0
                for leg in route["legs"]:
                    distancia_total_m += leg["distance"]["value"]  # en metros
                    duracion_total_s += leg["duration"]["value"]   # en segundos

                # Convertir a texto legible
                distancia_km = round(distancia_total_m / 1000, 2)
                horas = duracion_total_s // 3600
                minutos = (duracion_total_s % 3600) // 60
                duracion_texto = f"{horas}h {minutos}min" if horas > 0 else f"{minutos}min"

                # Crear el mapa
                ruta_map = folium.Map(location=[ny_lat, ny_lng], zoom_start=13)

                # Marcar origen y destino
                origen_coords = [route["legs"][0]["start_location"]["lat"], route["legs"][0]["start_location"]["lng"]]
                destino_coords = [route["legs"][0]["end_location"]["lat"], route["legs"][0]["end_location"]["lng"]]

                folium.Marker(origen_coords, tooltip="Origen", icon=folium.Icon(color="green")).add_to(ruta_map)
                folium.Marker(destino_coords, tooltip="Destino", icon=folium.Icon(color="red")).add_to(ruta_map)

                # Trazar la línea de la ruta
                folium.PolyLine(puntos, color="blue", weight=5, opacity=0.8).add_to(ruta_map)

                # Mostrar el mapa y resultados
                folium_static(ruta_map)

                st.success(f"🚗 Distance: {distancia_km} KM | ⏱️ Estimated duration: {duracion_texto}")
            else:
                st.error("The route could not be calculated. Please check the addresses you entered.")
        else:
            # Mapa estático si aún no se ha calculado
            mapa_base = folium.Map(location=[ny_lat, ny_lng], zoom_start=12)
            folium_static(mapa_base)
    
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