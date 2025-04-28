import unittest
import os
import requests


def login(username, password):
    url = "http://localhost:8000/login"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None


def test_login():
    token = login("admin@example.com", "admin")
    assert token is not None


def test_predict():
    token = login("admin@example.com", "admin")
    # Get the absolute path to the test image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "dog.jpeg")
    
    files = [("file", ("dog.jpeg", open(image_path, "rb"), "image/jpeg"))]
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        "http://localhost:8000/model/predict",
        headers=headers,
        files=files,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "prediction" in data
    assert "score" in data
    assert isinstance(data["score"], float)
    assert 0 <= data["score"] <= 1
