import datetime
from typing import Optional

import folium
import pandas as pd
import requests
import streamlit as st
from app.settings import API_BASE_URL, DEFAULT_MAP_LOCATION, DEFAULT_ZOOM, PAGE_ICON, PAGE_TITLE, GOOGLE_MAPS_API_KEY
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
        data (dict): prediction data including passenger_count and trip_distance

    Returns:
        requests.Response: response from the API
    """
    # Ensure we have the required fields
    if 'passenger_count' not in data:
        data['passenger_count'] = 1  # Default to 1 passenger
    
    if 'trip_distance' not in data:
        data['trip_distance'] = 1.0  # Default to 1 mile
    
    # Get current datetime for the pickup 
    if 'pickup_datetime' not in data:
        from datetime import datetime
        data['pickup_datetime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    url = f"{API_BASE_URL}/model/predict/fare_duration"
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        # Show errors if request fails
        if response.status_code != 200:
            st.error(f"API error: {response.status_code} - {response.text}")
        
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


def send_feedback(token: str, rating: int, comment: str, prediction_type: str, prediction_data: dict) -> requests.Response:
    """This function calls the feedback endpoint of the API to send feedback about
    the prediction.

    Args:
        token (str): token to authenticate the user
        rating (int): rating from 1 to 5
        comment (str): optional text feedback
        prediction_type (str): "fare_duration" or "demand"
        prediction_data (dict): the original prediction data

    Returns:
        requests.Response: response from the API
    """
    url = f"{API_BASE_URL}/feedback"
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Get the last prediction from session state if available
    last_prediction = st.session_state.get("last_prediction", {})
    
    feedback_data = {
        "rating": rating,
        "comment": comment,
        "prediction_type": prediction_type,
        "prediction_data": prediction_data,
        "last_prediction": last_prediction
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

        if not GOOGLE_MAPS_API_KEY:
            st.error("Google Maps API key is not configured. Please set the GOOGLE_MAPS_API_KEY environment variable.")
            st.stop()

        # Mostrar mapa base de Nueva York
        ny_lat, ny_lng = 40.7128, -74.0060

        # Initialize session state variables if not present
        if 'has_route' not in st.session_state:
            st.session_state.has_route = False
        if 'route_distance_km' not in st.session_state:
            st.session_state.route_distance_km = 0
        if 'route_distance_miles' not in st.session_state:
            st.session_state.route_distance_miles = 0
        if 'route_origin' not in st.session_state:
            st.session_state.route_origin = ""
        if 'route_destination' not in st.session_state:
            st.session_state.route_destination = ""
            
        # Define callback to handle route calculation
        def calculate_route(origin, destination):
            if not origin or not destination:
                st.error("Please enter both origin and destination addresses.")
                return False
                
            # Get coordinates
            lat1, lng1 = geocode_address(origin, GOOGLE_MAPS_API_KEY)
            lat2, lng2 = geocode_address(destination, GOOGLE_MAPS_API_KEY)
            
            if not lat1 or not lat2:
                st.error("Could not geocode one or both addresses. Please check them and try again.")
                return False
                
            # Call Google Maps Directions API
            directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={lat1},{lng1}&destination={lat2},{lng2}&mode=driving&key={GOOGLE_MAPS_API_KEY}"
            response = requests.get(directions_url)
            data = response.json()
            
            if data["status"] != "OK":
                st.error(f"Could not calculate route: {data['status']}")
                return False
                
            # Process route data
            route = data["routes"][0]
            puntos = polyline.decode(route["overview_polyline"]["points"])
            
            # Calculate total distance and duration
            distancia_total_m = 0
            duracion_total_s = 0
            for leg in route["legs"]:
                distancia_total_m += leg["distance"]["value"]  # meters
                duracion_total_s += leg["duration"]["value"]   # seconds
                
            # Convert to readable format
            distancia_km = round(distancia_total_m / 1000, 2)
            distancia_miles = round(distancia_km * 0.621371, 2)
            
            # Save to session state
            st.session_state.has_route = True
            st.session_state.route_distance_km = distancia_km
            st.session_state.route_distance_miles = distancia_miles
            st.session_state.route_origin = origin
            st.session_state.route_destination = destination
            st.session_state.route_points = puntos
            st.session_state.route_origin_coords = [route["legs"][0]["start_location"]["lat"], route["legs"][0]["start_location"]["lng"]]
            st.session_state.route_destination_coords = [route["legs"][0]["end_location"]["lat"], route["legs"][0]["end_location"]["lng"]]
            
            # Calculate human-readable duration
            horas = duracion_total_s // 3600
            minutos = (duracion_total_s % 3600) // 60
            st.session_state.route_duration_text = f"{horas}h {minutos}min" if horas > 0 else f"{minutos}min"
            
            # Print debug info
            print(f"\n==== ROUTE CALCULATED AND STORED ====")
            print(f"Origin: {origin} -> Destination: {destination}")
            print(f"Distance: {distancia_km} km / {distancia_miles} miles")
            print(f"Session state vars: {list(st.session_state.keys())}")
            
            return True
            
        # Section 1: Route input form - always visible
        with st.form(key="route_form"):
            col1, col2 = st.columns(2)
            with col1:
                origen = st.text_input("📍 Origin Address", 
                                      value=st.session_state.get('route_origin', ''),
                                      placeholder="E.g., Times Square, New York")
            with col2:
                destino = st.text_input("🏁 Destination Address", 
                                        value=st.session_state.get('route_destination', ''),
                                        placeholder="E.g., Central Park, New York")
            submit_button = st.form_submit_button(label="Calculate Route")
            
        # Process form submission
        if submit_button:
            calculate_route(origen, destino)
            
        # Section 2: Display map and route info if available
        if st.session_state.has_route:
            # Create map centered on the route's midpoint
            route_points = st.session_state.route_points
            
            # Calculate the bounds of the route
            lats = [point[0] for point in route_points]
            lngs = [point[1] for point in route_points]
            
            # Calculate center point
            center_lat = (min(lats) + max(lats)) / 2
            center_lng = (min(lngs) + max(lngs)) / 2
            
            # Adjust zoom based on route distance
            if st.session_state.route_distance_km < 2:
                zoom_level = 14
            elif st.session_state.route_distance_km < 5:
                zoom_level = 13
            elif st.session_state.route_distance_km < 10:
                zoom_level = 12
            else:
                zoom_level = 11
            
            # Create map with dynamic center and zoom
            ruta_map = folium.Map(location=[center_lat, center_lng], zoom_start=zoom_level)
            
            # Add markers and route line
            folium.Marker(
                st.session_state.route_origin_coords, 
                tooltip="Origin", 
                icon=folium.Icon(color="green")
            ).add_to(ruta_map)
            
            folium.Marker(
                st.session_state.route_destination_coords, 
                tooltip="Destination", 
                icon=folium.Icon(color="red")
            ).add_to(ruta_map)
            
            folium.PolyLine(
                st.session_state.route_points, 
                color="blue", 
                weight=5, 
                opacity=0.8
            ).add_to(ruta_map)
            
            # Fit map to bounds of route
            ruta_map.fit_bounds([[min(lats), min(lngs)], [max(lats), max(lngs)]])
            
            # Display map
            folium_static(ruta_map)
            
            # Show route details
            route_info = f"""
            **Route:** {st.session_state.route_origin} → {st.session_state.route_destination}  
            **Distance:** {st.session_state.route_distance_km} km ({st.session_state.route_distance_miles} miles)  
            **Est. Duration:** {st.session_state.route_duration_text}
            """
            st.success(route_info)
            
            # Section 3: Prediction controls - only shown when route is available
            st.subheader("Get fare and duration prediction")
            passenger_count = st.select_slider(
                "👥 Passenger Count",
                options=[1, 2, 3, 4],
                value=1
            )
            
            if st.button("🔮 Predict Fare & Duration"):
                # Create prediction request
                prediction_data = {
                    "passenger_count": passenger_count,
                    "trip_distance": st.session_state.route_distance_miles
                }
                
                response = predict_fare_duration(token, prediction_data)
                
                if response and response.status_code == 200:
                    try:
                        result = response.json()
                        
                        # Extract prediction values
                        fare_amount = float(result.get('fare_amount', 0))
                        trip_duration = float(result.get('trip_duration', 0))
                        
                        # Create prediction summary box with updated background color
                        prediction_html = f"""
                        <div style="padding:15px; border-radius:10px; background-color:#2E4053; color:white; margin:10px 0;">
                            <h3 style="margin-top:0; color:white;">Prediction Results</h3>
                            <p>For your <b>{st.session_state.route_distance_miles} mile</b> trip with <b>{passenger_count}</b> passenger(s):</p>
                        </div>
                        """
                        st.markdown(prediction_html, unsafe_allow_html=True)
                        
                        # Display metrics
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("💰 Estimated Fare", f"${fare_amount:.2f}")
                        with col2:
                            st.metric("⏱️ Estimated Duration", f"{trip_duration/60:.1f} min")
                        
                        # Store for feedback
                        st.session_state.last_prediction = {
                            'fare_amount': fare_amount,
                            'trip_duration': trip_duration,
                            'success': True
                        }
                        st.session_state.last_prediction_data = prediction_data
                        st.session_state.last_prediction_type = "fare_duration"
                        
                    except Exception as e:
                        st.error(f"Error processing prediction: {str(e)}")
                else:
                    st.error("Failed to get prediction. Please try again.")
        else:
            # Show empty map when no route is calculated
            mapa_base = folium.Map(location=[ny_lat, ny_lng], zoom_start=12)
            folium_static(mapa_base)
            
            st.info("Enter origin and destination addresses above and click 'Calculate Route' to get started.")
            
            # Allow manual distance input when no route is available
            st.subheader("Or make a prediction with manual distance input")
            
            col1, col2 = st.columns(2)
            with col1:
                manual_distance = st.number_input("🛣️ Trip Distance (miles)", 
                                               min_value=0.1, 
                                               value=1.0, 
                                               step=0.1)
            with col2:
                manual_passengers = st.select_slider(
                    "👥 Passenger Count",
                    options=[1, 2, 3, 4],
                    value=1
                )
                
            if st.button("🔮 Predict with Manual Input"):
                # Create prediction data
                prediction_data = {
                    "passenger_count": manual_passengers,
                    "trip_distance": manual_distance
                }
                
                # Call prediction API
                response = predict_fare_duration(token, prediction_data)
                
                if response and response.status_code == 200:
                    try:
                        result = response.json()
                        
                        # Extract prediction values
                        fare_amount = float(result.get('fare_amount', 0))
                        trip_duration = float(result.get('trip_duration', 0))
                        
                        # Create prediction summary box with updated background color
                        prediction_html = f"""
                        <div style="padding:15px; border-radius:10px; background-color:#2E4053; color:white; margin:10px 0;">
                            <h3 style="margin-top:0; color:white;">Prediction Results</h3>
                            <p>For your <b>{manual_distance} mile</b> trip with <b>{manual_passengers}</b> passenger(s):</p>
                        </div>
                        """
                        st.markdown(prediction_html, unsafe_allow_html=True)
                        
                        # Display metrics
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("💰 Estimated Fare", f"${fare_amount:.2f}")
                        with col2:
                            st.metric("⏱️ Estimated Duration", f"{trip_duration/60:.1f} min")
                        
                        # Store for feedback
                        st.session_state.last_prediction = {
                            'fare_amount': fare_amount,
                            'trip_duration': trip_duration,
                            'success': True
                        }
                        st.session_state.last_prediction_data = prediction_data
                        st.session_state.last_prediction_type = "fare_duration"
                        
                    except Exception as e:
                        st.error(f"Error processing prediction: {str(e)}")
                else:
                    st.error("Failed to get prediction. Please try again.")
    
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
        
        # Add some spacing and separator
        st.markdown("<hr style='margin: 15px 0; border-top: 1px solid #505050;'>", unsafe_allow_html=True)
        
        # Display rating instructions with styling that matches the prediction results
        st.markdown("""
        <h3 style='margin-bottom: 15px; color: #FFDD00;'>How would you rate this prediction?</h3>
        <p style='color: #e0e0e0; margin-bottom: 20px;'>Click a star to rate (1-5)</p>
        """, unsafe_allow_html=True)
        
        # Create columns for star buttons with equal spacing
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # Individual star buttons with different help text and larger font
        button_style = """
        <style>
        div[data-testid="stButton"] button {
            font-size: 32px;
            padding: 5px 15px;
            background-color: #34495E;
            color: #FFDD00;
            border: none;
            transition: transform 0.2s, background-color 0.2s;
        }
        div[data-testid="stButton"] button:hover {
            transform: scale(1.1);
            background-color: #2C3E50;
        }
        </style>
        """
        st.markdown(button_style, unsafe_allow_html=True)
        
        with col1:
            star1 = st.button("⭐", key="star1", help="Rate 1 - Poor")
        with col2:
            star2 = st.button("⭐", key="star2", help="Rate 2 - Fair")
        with col3:
            star3 = st.button("⭐", key="star3", help="Rate 3 - Good")
        with col4:
            star4 = st.button("⭐", key="star4", help="Rate 4 - Very Good")
        with col5:
            star5 = st.button("⭐", key="star5", help="Rate 5 - Excellent")
        
        # Determine rating based on which star button was clicked
        if star1:
            st.session_state.feedback_rating = 1
        elif star2:
            st.session_state.feedback_rating = 2
        elif star3:
            st.session_state.feedback_rating = 3
        elif star4:
            st.session_state.feedback_rating = 4
        elif star5:
            st.session_state.feedback_rating = 5
        
        # Show the current rating with a visual representation
        if 'feedback_rating' in st.session_state:
            rating = st.session_state.feedback_rating
            
            # Rating descriptions
            rating_descriptions = {
                1: "Poor",
                2: "Fair",
                3: "Good", 
                4: "Very Good",
                5: "Excellent"
            }
            
            # Create a visually appealing rating display
            filled_stars = "⭐" * rating
            empty_stars = "☆" * (5 - rating)
            
            # Use colors that match the dark theme of prediction results
            accent_colors = {
                1: "#FF5252",  # red accent
                2: "#FF9800",  # orange accent
                3: "#FFEB3B",  # yellow accent
                4: "#4CAF50",  # green accent
                5: "#00BCD4"   # blue accent
            }
            
            rating_display = f"""
            <div style="background-color: #2E4053; padding: 20px; border-radius: 10px; text-align: center; margin: 25px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                <div style="font-size: 18px; margin-bottom: 8px; color: white;">You rated this prediction: <strong style="color: {accent_colors[rating]};">{rating}/5</strong></div>
                <div style="font-size: 30px; margin: 15px 0; color: {accent_colors[rating]};">{filled_stars}{empty_stars}</div>
                <div style="font-style: italic; margin-top: 8px; color: {accent_colors[rating]};">{rating_descriptions[rating]}</div>
            </div>
            """
            st.markdown(rating_display, unsafe_allow_html=True)
        
        # Add some spacing before the comments section
        st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)
        
        # Optional comment field with improved styling
        st.markdown("""
        <h3 style='margin-bottom: 5px; color: #FFDD00;'>Additional Comments (Optional)</h3>
        <p style='font-style: italic; color: #e0e0e0; margin-bottom: 15px;'>Share your thoughts about the prediction</p>
        """, unsafe_allow_html=True)
        
        comment = st.text_area(
            "",
            key="feedback_comment",
            height=100,
            placeholder="Enter your comments here..."
        )
        
        # Send feedback button with more prominent styling
        send_button = st.button("Submit Feedback", type="primary")
        if send_button:
            if 'feedback_rating' in st.session_state:
                with st.spinner("Sending feedback..."):
                    response = send_feedback(
                        token=token,
                        rating=st.session_state.feedback_rating,
                        comment=comment,
                        prediction_type=st.session_state.last_prediction_type,
                        prediction_data=st.session_state.last_prediction_data
                    )
                
                if response and response.status_code in (200, 201):
                    st.success("Thanks for your feedback! Your input helps us improve our predictions.")
                    # Clear the rating after submission
                    if 'feedback_rating' in st.session_state:
                        del st.session_state.feedback_rating
                else:
                    if response:
                        st.error(f"Error sending feedback: {response.text}")
                    else:
                        st.error("Error sending feedback. Please try again.")
            else:
                st.warning("Please select a star rating before submitting your feedback.")
    
    # Logout button
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

    # In the sidebar section, after the page selection and before the logout button
    if st.sidebar.checkbox("Show API Test"):
        st.sidebar.header("API Test")
        
        # Simple form to test the API directly
        sidebar_passengers = st.sidebar.slider("Test Passengers", min_value=1, max_value=4, value=1)
        sidebar_distance = st.sidebar.number_input("Test Distance (miles)", min_value=0.1, value=1.0, step=0.1)
        
        if st.sidebar.button("Test API Directly"):
            test_data = {
                "passenger_count": sidebar_passengers,
                "trip_distance": sidebar_distance
            }
            
            test_response = predict_fare_duration(token, test_data)
            if test_response and test_response.status_code == 200:
                test_result = test_response.json()
                st.sidebar.json(test_result)
                st.sidebar.success(f"Raw API Test Result: fare=${test_result.get('fare_amount', 0):.2f}, duration={test_result.get('trip_duration', 0)/60:.1f}min")
            else:
                if test_response:
                    st.sidebar.error(f"API Test Failed: {test_response.status_code} - {test_response.text}")
                else:
                    st.sidebar.error("API Test Failed")

# Footer
st.markdown("<hr style='border:2px solid #FFDD00;'>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #FFDD00;'>NYC Taxi Prediction System</p>",
    unsafe_allow_html=True,
) 