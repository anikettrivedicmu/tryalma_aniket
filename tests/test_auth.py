import pytest
from fastapi import status

def test_login_success(client, test_user):
    login_data = {
        "username": "test@example.com",
        "password": "test"
    }
    response = client.post("/api/v1/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    login_data = {
        "username": "test@example.com",
        "password": "wrong"
    }
    response = client.post("/api/v1/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_wrong_email(client, test_user):
    login_data = {
        "username": "wrong@example.com",
        "password": "test"
    }
    response = client.post("/api/v1/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, test_auth_headers, test_user):
    response = client.get("/api/v1/me", headers=test_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == test_user.email

def test_get_current_user_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED