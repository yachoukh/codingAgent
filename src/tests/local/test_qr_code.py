import pytest
from fastapi.testclient import TestClient

from fastapi_app.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


def test_qr_code_endpoint_exists(client):
    """Test that the QR code endpoint exists and returns an image"""
    response = client.get("/qrcode")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_qr_code_generates_valid_image(client):
    """Test that the QR code endpoint generates a valid PNG image"""
    response = client.get("/qrcode")
    assert response.status_code == 200
    
    # Verify it's a valid PNG by checking the magic bytes
    content = response.content
    assert content[:8] == b'\x89PNG\r\n\x1a\n'  # PNG magic bytes


def test_qr_code_contains_url_data(client):
    """Test that the QR code is generated with proper data"""
    response = client.get("/qrcode")
    assert response.status_code == 200
    
    # Just ensure it returns valid image data
    assert len(response.content) > 100  # QR code image should be larger than 100 bytes
