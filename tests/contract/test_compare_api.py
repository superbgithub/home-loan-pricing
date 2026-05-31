"""Contract tests for POST /price/compare."""
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


_30YR = {
    "scenario_id": "30yr",
    "loan_type": "fixed",
    "home_price": "400000.00",
    "down_payment": "80000.00",
    "term_years": 30,
    "annual_rate": "6.50",
}

_15YR = {
    "scenario_id": "15yr",
    "loan_type": "fixed",
    "home_price": "400000.00",
    "down_payment": "80000.00",
    "term_years": 15,
    "annual_rate": "6.00",
}

_INVALID = {
    "scenario_id": "bad",
    "loan_type": "fixed",
    "home_price": "400000.00",
    "down_payment": "80000.00",
    "term_years": 30,
    "annual_rate": "99.00",  # > 30 → invalid
}


class TestComparePriceContract:
    async def test_two_valid_scenarios_returns_200(self, client):
        resp = await client.post(
            "/api/v1/price/compare",
            json={"scenarios": [_30YR, _15YR]},
        )
        assert resp.status_code == 200

    async def test_two_results_returned(self, client):
        resp = await client.post(
            "/api/v1/price/compare",
            json={"scenarios": [_30YR, _15YR]},
        )
        body = resp.json()
        assert len(body["results"]) == 2

    async def test_results_have_scenario_ids(self, client):
        resp = await client.post(
            "/api/v1/price/compare",
            json={"scenarios": [_30YR, _15YR]},
        )
        ids = {r["scenario_id"] for r in resp.json()["results"]}
        assert "30yr" in ids
        assert "15yr" in ids

    async def test_partial_success_mixed_results(self, client):
        resp = await client.post(
            "/api/v1/price/compare",
            json={"scenarios": [_30YR, _INVALID]},
        )
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert len(results) == 2
        errors = [r for r in results if r.get("error")]
        successes = [r for r in results if not r.get("error")]
        assert len(errors) == 1
        assert len(successes) == 1

    async def test_exceeding_limit_returns_422(self, client):
        resp = await client.post(
            "/api/v1/price/compare",
            json={"scenarios": [_30YR] * 6},
        )
        assert resp.status_code == 422

    async def test_empty_scenarios_returns_422(self, client):
        resp = await client.post(
            "/api/v1/price/compare",
            json={"scenarios": []},
        )
        assert resp.status_code == 422
