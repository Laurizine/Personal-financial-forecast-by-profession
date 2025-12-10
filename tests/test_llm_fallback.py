import pytest
from unittest.mock import patch
from app.controller import CreditController

def test_llm_exception_handling():
    controller = CreditController()
    payload = {
        "job": "Test",
        "income_monthly": 1000,
        "expense_monthly": 500
    }
    
    # Mock generate_explanation to raise Exception
    with patch("app.controller.generate_explanation") as mock_gen:
        mock_gen.side_effect = RuntimeError("Gemini API overloaded")
        
        result = controller.process(payload)
        
        # Verify result contains error message instead of crashing
        assert "Lỗi Gemini: Gemini API overloaded" in result["llm_explanation"]
        
        # Other parts should still work
        assert "final_class" in result
