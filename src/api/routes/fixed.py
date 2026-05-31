from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from fastapi import APIRouter
from pydantic import ValidationError

from src.audit.logger import audit_context
from src.engine.amortisation import calculate_monthly_payment
from src.engine.apr import calculate_apr
from src.models.inputs import FixedScenario, _resolve_down_payment
from src.models.outputs import PricingResult

router = APIRouter()


@router.post("/price/fixed", response_model=PricingResult)
async def price_fixed(scenario: FixedScenario) -> PricingResult:
    loan_amount = scenario.loan_amount()
    fees = [f.amount for f in scenario.fee_schedule.fees]

    inputs_payload: Dict[str, Any] = {
        "loan_type": "fixed",
        "home_price": str(scenario.home_price),
        "down_payment": str(scenario.down_payment),
        "term_years": scenario.term_years,
        "annual_rate": str(scenario.annual_rate),
    }

    with audit_context("fixed", 1, inputs_payload) as record:
        monthly = calculate_monthly_payment(loan_amount, scenario.annual_rate, scenario.term_years)
        apr = calculate_apr(loan_amount, monthly, scenario.term_years * 12, fees)
        total_interest = (monthly * scenario.term_years * 12 - loan_amount).quantize(
            Decimal("0.01")
        )
        result = PricingResult(
            scenario_id=scenario.scenario_id,
            loan_type="fixed",
            loan_amount=loan_amount,
            monthly_payment=monthly,
            apr=apr,
            total_interest=total_interest,
            rate_type_label=f"Fixed {scenario.term_years}-year",
            parameters_summary=inputs_payload,
        )
        record["outputs_summary"] = {
            "monthly_payment": str(monthly),
            "apr": str(apr),
        }

    return result
