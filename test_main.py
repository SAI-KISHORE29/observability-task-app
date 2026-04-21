from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_invalid_input():
    # Sending missing fields according to OrderCreate model
    response = client.post("/orders", json={
        "productId": "prod456",
        "quantity": 2
        # missing customer and items
    })

    assert response.status_code == 400
    assert "error" in response.json()