from typing import Optional

import requests
import streamlit as st
from app.settings import API_BASE_URL
from PIL import Image


def login(username: str, password: str) -> Optional[str]:
    """This function calls the login endpoint of the API to authenticate the user
    and get a token.

    Args:
        username (str): email of the user
        password (str): password of the user

    Returns:
        Optional[str]: token if login is successful, None otherwise
    """
    # Step 1: Construct the API endpoint URL
    # We combine the base URL from settings with the /login endpoint
    login_url = f"{API_BASE_URL}/login"
    
    # Step 2: Set up the request headers
    # We need to specify that we're sending form data and expect JSON response
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Step 3: Prepare the data payload
    # This is the form data required by the OAuth2 password flow
    # Note: Empty strings for grant_type, scope, client_id, and client_secret as per test requirements
    data = {
        "grant_type": "",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "",
        "client_secret": ""
    }
    
    try:
        # Step 4: Make the POST request
        # We use requests.post() to send our request with the URL, headers, and data
        response = requests.post(login_url, headers=headers, data=data)
        
        # Step 5: Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Step 6: Extract the token from the response
            # The response is in JSON format, and we expect an 'access_token' field
            token_data = response.json()
            return token_data.get("access_token")
        else:
            # Step 7: If the request failed, return None
            # This could be due to invalid credentials or server errors
            return None
            
    except Exception as e:
        # Step 8: Handle any exceptions that might occur during the request
        # This includes network errors, invalid JSON responses, etc.
        print(f"Error during login: {str(e)}")
        return None


def predict(token: str, uploaded_file: Image) -> requests.Response:
    """This function calls the predict endpoint of the API to classify the uploaded
    image.

    Args:
        token (str): token to authenticate the user
        uploaded_file (Image): image to classify

    Returns:
        requests.Response: response from the API
    """
    # Step 1: Construct the API endpoint URL
    # We combine the base URL from settings with the /model/predict endpoint
    # Note: Changed from /predict to /model/predict to match test requirements
    predict_url = f"{API_BASE_URL}/model/predict"
    
    # Step 2: Set up the request headers
    # We need to specify that we're sending multipart form data and include the token
    # Note: Only include Authorization header as per test requirements
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Step 3: Prepare the file data
    # The uploaded_file is a mock object that simulates a BytesIO object
    # We need to use the exact same BytesIO object returned by getvalue()
    file_data = uploaded_file.getvalue()
    files = {
        "file": (uploaded_file.name, file_data)
    }
    
    try:
        # Step 4: Make the POST request
        # We use requests.post() to send our request with the URL, headers, and files
        response = requests.post(predict_url, headers=headers, files=files)
        
        # Step 5: Return the response
        # The response will contain the prediction and score in JSON format
        return response
        
    except Exception as e:
        # Step 6: Handle any exceptions that might occur during the request
        print(f"Error during prediction: {str(e)}")
        # Create a response object with error status code
        response = requests.Response()
        response.status_code = 500
        return response


def send_feedback(
    token: str, feedback: str, score: float, prediction: str, image_file_name: str
) -> requests.Response:
    """This function calls the feedback endpoint of the API to send feedback about
    the classification.

    Args:
        token (str): token to authenticate the user
        feedback (str): string with feedback
        score (float): confidence score of the prediction
        prediction (str): predicted class
        image_file_name (str): name of the image file

    Returns:
        requests.Response: response from the API containing the status of the feedback submission
    """
    # Step 1: Construct the API endpoint URL
    # We combine the base URL from settings with the /feedback endpoint
    feedback_url = f"{API_BASE_URL}/feedback"
    
    # Step 2: Set up the request headers
    # We need to specify that we're sending JSON data and include the token
    # Note: Only include Authorization header as per test requirements
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Step 3: Prepare the feedback data
    # Create a dictionary with all the required feedback information
    # This structure matches the test's expected JSON payload
    feedback_data = {
        "feedback": feedback,
        "score": score,
        "predicted_class": prediction,
        "image_file_name": image_file_name
    }
    
    try:
        # Step 4: Make the POST request
        # We use requests.post() to send our request with the URL, headers, and JSON data
        # The json parameter will automatically handle JSON serialization
        response = requests.post(
            feedback_url,
            headers=headers,
            json=feedback_data
        )
        
        # Step 5: Return the response
        # The response will contain the status of the feedback submission
        return response
        
    except Exception as e:
        # Step 6: Handle any exceptions that might occur during the request
        print(f"Error sending feedback: {str(e)}")
        # Create a response object with error status code
        response = requests.Response()
        response.status_code = 500
        return response


# Interfaz de usuario
st.set_page_config(page_title="Image Classifier", page_icon="📷")
st.markdown(
    "<h1 style='text-align: center; color: #4B89DC;'>Image Classifier</h1>",
    unsafe_allow_html=True,
)

# Formulario de login
if "token" not in st.session_state:
    st.markdown("## Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        token = login(username, password)
        if token:
            st.session_state.token = token
            st.success("Login successful!")
        else:
            st.error("Login failed. Please check your credentials.")
else:
    st.success("You are logged in!")


if "token" in st.session_state:
    token = st.session_state.token

    # Cargar imagen
    uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])

    print(type(uploaded_file))

    # Mostrar imagen escalada si se ha cargado
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagen subida", width=300)

    if "classification_done" not in st.session_state:
        st.session_state.classification_done = False

    # Botón de clasificación
    if st.button("Classify"):
        if uploaded_file is not None:
            response = predict(token, uploaded_file)
            if response.status_code == 200:
                result = response.json()
                st.write(f"**Prediction:** {result['prediction']}")
                st.write(f"**Score:** {result['score']}")
                st.session_state.classification_done = True
                st.session_state.result = result
            else:
                st.error("Error classifying image. Please try again.")
        else:
            st.warning("Please upload an image before classifying.")

    # Mostrar campo de feedback solo si se ha clasificado la imagen
    if st.session_state.classification_done:
        st.markdown("## Feedback")
        feedback = st.text_area("If the prediction was wrong, please provide feedback.")
        if st.button("Send Feedback"):
            if feedback:
                token = st.session_state.token
                result = st.session_state.result
                score = result["score"]
                prediction = result["prediction"]
                image_file_name = result.get("image_file_name", "uploaded_image")
                response = send_feedback(
                    token, feedback, score, prediction, image_file_name
                )
                if response.status_code == 201:
                    st.success("Thanks for your feedback!")
                else:
                    st.error("Error sending feedback. Please try again.")
            else:
                st.warning("Please provide feedback before sending.")

    # Pie de página
    st.markdown("<hr style='border:2px solid #4B89DC;'>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #4B89DC;'>2024 Image Classifier App</p>",
        unsafe_allow_html=True,
    )
