from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from fastapi import APIRouter

from src.audit.logger import audit_context
from src.engine.arm import calculate_arm_apr, calculate_arm_initial_payment
from src.models.inputs import ArmScenario
from src.models.outputs import PricingResult

router = APIRouter()


@router.post("/price/arm", response_model=PricingResult)
async def price_arm(scenario: ArmScenario) -> PricingResult:
    loan_amount = scenario.loan_amount()
    fees = [f.amount for f in scenario.fee_schedule.fees]
    p = scenario.arm_params

    inputs_payload: Dict[str, Any] = {
        "loan_type": "arm",
        "home_price": str(scenario.home_price),
        "down_payment": str(scenario.down_payment),
        "term_years": scenario.term_years,
        "initial_rate": str(scenario.initial_rate),
        "arm_params": {
            "fixed_period_years": p.fixed_period_years,
            "adjustment_period_years": p.adjustment_period_years,
            "initial_cap": str(p.initial_cap),
            "periodic_cap": str(p.periodic_cap),
            "lifetime_cap": str(p.lifetime_cap),
        },
    }

    with audit_context("arm", 1, inputs_payload) as record:
        monthly = calculate_arm_initial_payment(
            loan_amount, scenario.initial_rate, scenario.term_years
        )
        apr = calculate_arm_apr(loan_amount, monthly, scenario.term_years * 12, fees)
        total_interest = (monthly * scenario.term_years * 12 - loan_amount).quantize(
            Decimal("0.01")
        )
        label = f"{p.fixed_period_years}/{p.adjustment_period_years} ARM {scenario.term_years}-year"
        result = PricingResult(
            scenario_id=scenario.scenario_id,
            loan_type="arm",
            loan_amount=loan_amount,
            monthly_payment=monthly,
            apr=apr,
            total_interest=total_interest,
            rate_type_label=label,
            parameters_summary=inputs_payload,
        )
        record["outputs_summary"] = {
            "monthly_payment": str(monthly),
            "apr": str(apr),
        }

    return result
