from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}

def test_explain_endpoint():
    payload = {
        "job": "Tester",
        "income_monthly": 15000000,
        "expense_monthly": 8000000,
        "debt_amount": 0,
        "late_payments_12m": 0,
        "credit_history_length_years": 5,
        "new_credit_accounts": 0,
        "credit_mix": "good"
    }
    response = client.post("/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "final_class" in data
    assert "explanation" in data
    assert data["facts"]["income_monthly"] == 15000000
