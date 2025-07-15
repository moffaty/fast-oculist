from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/test")
    assert response.status_code == 200
    assert "test" in response.text
