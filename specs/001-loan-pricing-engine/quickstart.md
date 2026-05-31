# Quickstart: Loan Pricing Engine

**Branch**: `001-loan-pricing-engine` | **Date**: 2026-05-30

Use this guide to verify the engine works end-to-end after implementation.

---

## Prerequisites

- Python 3.11+
- `pip` (or `pip3`)

---

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 2. Start the service

```bash
uvicorn src.api.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 3. Verify health

```bash
curl http://localhost:8000/api/v1/health
```

Expected:
```json
{"status": "ok"}
```

---

## 4. Price a fixed-rate loan

```bash
curl -s -X POST http://localhost:8000/api/v1/price/fixed \
  -H "Content-Type: application/json" \
  -d '{
    "home_price": "400000.00",
    "down_payment": "80000.00",
    "term_years": 30,
    "annual_rate": "6.50"
  }' | python3 -m json.tool
```

Expected (monthly_payment rounded to cents, apr matches rate with no fees):
```json
{
  "loan_type": "fixed",
  "loan_amount": "320000.00",
  "monthly_payment": "2022.65",
  "apr": "6.50",
  "rate_type_label": "Fixed 30-year"
}
```

---

## 5. Price an ARM loan

```bash
curl -s -X POST http://localhost:8000/api/v1/price/arm \
  -H "Content-Type: application/json" \
  -d '{
    "home_price": "350000.00",
    "down_payment": "70000.00",
    "term_years": 30,
    "initial_rate": "5.75",
    "arm_params": {
      "fixed_period_years": 5,
      "adjustment_period_years": 1,
      "initial_cap": "2.00",
      "periodic_cap": "2.00",
      "lifetime_cap": "5.00"
    }
  }' | python3 -m json.tool
```

Expected:
```json
{
  "loan_type": "arm",
  "loan_amount": "280000.00",
  "rate_type_label": "5/1 ARM 30-year"
}
```

---

## 6. Compare two scenarios

```bash
curl -s -X POST http://localhost:8000/api/v1/price/compare \
  -H "Content-Type: application/json" \
  -d '{
    "scenarios": [
      {
        "scenario_id": "30yr",
        "loan_type": "fixed",
        "home_price": "400000.00",
        "down_payment": "80000.00",
        "term_years": 30,
        "annual_rate": "6.50"
      },
      {
        "scenario_id": "15yr",
        "loan_type": "fixed",
        "home_price": "400000.00",
        "down_payment": "80000.00",
        "term_years": 15,
        "annual_rate": "6.00"
      }
    ]
  }' | python3 -m json.tool
```

Expected: two results in `results` array, each with `scenario_id`, `monthly_payment`,
`apr`, and `total_interest`.

---

## 7. Run tests

```bash
pytest tests/ -v
```

All tests should pass. TDD: ensure tests were written and failed before this step.

---

## 8. Verify audit output

Run any pricing request and check stdout for a single JSON audit line, e.g.:

```json
{"request_id": "...", "timestamp": "2026-05-30T...", "loan_type": "fixed",
 "scenario_count": 1, "inputs_hash": "...", "outputs_summary": {...},
 "duration_ms": 4, "error": null}
```

Every request MUST produce exactly one audit line.
