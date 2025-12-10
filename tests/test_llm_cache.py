import unittest
import os

from app.controller import CreditController
import llm.explanation_service as es


class TestLLMCache(unittest.TestCase):
    def setUp(self):
        self._orig_call = es.call_gemini
        self.calls = {"n": 0}

        def fake_call(prompt: str):
            self.calls["n"] += 1
            return "cached-ok"

        es.call_gemini = fake_call
        os.environ["GEMINI_MODEL"] = "gemini-2.0-flash-lite"

    def tearDown(self):
        es.call_gemini = self._orig_call

    def test_cache_explanation_same_input(self):
        controller = CreditController()
        payload = {
            "job": "IT Engineer",
            "income_monthly": 20000000,
            "expense_monthly": 12000000,
            "debt_amount": 6000000,
            "late_payments_12m": 1,
            "credit_history_length_years": 6,
            "new_credit_accounts": 2,
            "credit_mix": "fair",
        }

        r1 = controller.process(payload)
        r2 = controller.process(payload)

        self.assertEqual(self.calls["n"], 1)
        self.assertEqual(r1["llm_explanation"], "cached-ok")
        self.assertEqual(r2["llm_explanation"], "cached-ok")

    def test_retry_on_429(self):
        es.call_gemini = self._orig_call

        class MockModel:
            def __init__(self):
                self.attempts = 0
            def generate_content(self, prompt):
                self.attempts += 1
                raise RuntimeError("429 ResourceExhausted")

        orig_get_model = es._get_model
        mock_model = MockModel()
        es._get_model = lambda: mock_model

        with self.assertRaises(RuntimeError) as ctx:
            es.call_gemini("test prompt")
        self.assertIn("rate-limit", str(ctx.exception).lower())
        self.assertEqual(mock_model.attempts, 1)
        es._get_model = orig_get_model

    def test_retry_on_network_error(self):
        es.call_gemini = self._orig_call

        class MockModel:
            def __init__(self):
                self.attempts = 0
            def generate_content(self, prompt):
                self.attempts += 1
                if self.attempts < 3:
                    raise RuntimeError("connection lost")
                class Res:
                    text = "retry-success"
                return Res()

        orig_get_model = es._get_model
        mock_model = MockModel()
        es._get_model = lambda: mock_model
        orig_sleep = es.time.sleep
        es.time.sleep = lambda x: None

        try:
            res = es.call_gemini("test prompt")
            self.assertEqual(res, "retry-success")
            self.assertEqual(mock_model.attempts, 3)
        finally:
            es._get_model = orig_get_model
            es.time.sleep = orig_sleep


if __name__ == "__main__":
    unittest.main()
