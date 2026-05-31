"""Contract tests for POST /price/arm."""
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


_VALID_ARM = {
    "home_price": "350000.00",
    "down_payment": "70000.00",
    "term_years": 30,
    "initial_rate": "5.75",
    "arm_params": {
        "fixed_period_years": 5,
        "adjustment_period_years": 1,
        "initial_cap": "2.00",
        "periodic_cap": "2.00",
        "lifetime_cap": "5.00",
    },
}


class TestArmPriceContract:
    async def test_valid_arm_returns_200(self, client):
        resp = await client.post("/api/v1/price/arm", json=_VALID_ARM)
        assert resp.status_code == 200

    async def test_response_contains_required_fields(self, client):
        resp = await client.post("/api/v1/price/arm", json=_VALID_ARM)
        body = resp.json()
        assert "monthly_payment" in body
        assert "apr" in body
        assert body["loan_type"] == "arm"
        assert body["rate_type_label"] == "5/1 ARM 30-year"

    async def test_loan_amount_correct(self, client):
        resp = await client.post("/api/v1/price/arm", json=_VALID_ARM)
        assert resp.json()["loan_amount"] == "280000.00"

    async def test_inconsistent_caps_returns_422(self, client):
        bad = dict(_VALID_ARM)
        bad["arm_params"] = dict(_VALID_ARM["arm_params"])
        bad["arm_params"]["periodic_cap"] = "6.00"  # > lifetime_cap 5.00
        resp = await client.post("/api/v1/price/arm", json=bad)
        assert resp.status_code == 422

    async def test_fixed_period_exceeds_term_returns_422(self, client):
        bad = dict(_VALID_ARM)
        bad["term_years"] = 5  # fixed_period_years == term_years → invalid
        resp = await client.post("/api/v1/price/arm", json=bad)
        assert resp.status_code == 422
