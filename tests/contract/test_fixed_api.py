"""Contract tests for POST /price/fixed."""
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


class TestFixedPriceContract:
    async def test_valid_request_returns_200(self, client):
        resp = await client.post(
            "/api/v1/price/fixed",
            json={
                "home_price": "400000.00",
                "down_payment": "80000.00",
                "term_years": 30,
                "annual_rate": "6.50",
            },
        )
        assert resp.status_code == 200

    async def test_response_contains_required_fields(self, client):
        resp = await client.post(
            "/api/v1/price/fixed",
            json={
                "home_price": "400000.00",
                "down_payment": "80000.00",
                "term_years": 30,
                "annual_rate": "6.50",
            },
        )
        body = resp.json()
        assert "monthly_payment" in body
        assert "apr" in body
        assert "loan_type" in body
        assert body["loan_type"] == "fixed"

    async def test_correct_monthly_payment(self, client):
        resp = await client.post(
            "/api/v1/price/fixed",
            json={
                "home_price": "400000.00",
                "down_payment": "80000.00",
                "term_years": 30,
                "annual_rate": "6.50",
            },
        )
        assert resp.json()["monthly_payment"] == "2022.62"

    async def test_invalid_rate_returns_422(self, client):
        resp = await client.post(
            "/api/v1/price/fixed",
            json={
                "home_price": "400000.00",
                "down_payment": "80000.00",
                "term_years": 30,
                "annual_rate": "35.00",
            },
        )
        assert resp.status_code == 422

    async def test_down_payment_as_percentage(self, client):
        resp = await client.post(
            "/api/v1/price/fixed",
            json={
                "home_price": "400000.00",
                "down_payment": "20%",
                "term_years": 30,
                "annual_rate": "6.50",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["loan_amount"] == "320000.00"
