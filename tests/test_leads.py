import pytest
from fastapi import status
from app.models.lead import LeadStatus

def test_create_lead(client):
    # Test data
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
    }
    files = {
        "resume": ("test.pdf", b"test content", "application/pdf")
    }
    
    response = client.post("/api/v1/leads/", data=data, files=files)
    assert response.status_code == status.HTTP_200_OK
    
    result = response.json()
    assert result["first_name"] == data["first_name"]
    assert result["last_name"] == data["last_name"]
    assert result["email"] == data["email"]
    assert result["status"] == LeadStatus.PENDING.value
    assert "resume_path" in result

def test_get_leads_unauthorized(client):
    response = client.get("/api/v1/leads/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_leads_authorized(client, test_auth_headers):
    response = client.get("/api/v1/leads/", headers=test_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_update_lead_status(client, test_auth_headers, test_db):
    # First create a lead
    data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com"
    }
    files = {
        "resume": ("test.pdf", b"test content", "application/pdf")
    }
    
    create_response = client.post("/api/v1/leads/", data=data, files=files)
    lead_id = create_response.json()["id"]
    
    # Update status
    update_data = {"status": LeadStatus.REACHED_OUT.value}
    response = client.patch(
        f"/api/v1/leads/{lead_id}/status",
        json=update_data,
        headers=test_auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == LeadStatus.REACHED_OUT.value

def test_get_lead_not_found(client, test_auth_headers):
    response = client.get("/api/v1/leads/999", headers=test_auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND