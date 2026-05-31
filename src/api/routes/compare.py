from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List
from uuid import uuid4

from fastapi import APIRouter
from pydantic import ValidationError

from src.audit.logger import audit_context
from src.engine.arm import calculate_arm_apr, calculate_arm_initial_payment
from src.engine.amortisation import calculate_monthly_payment
from src.engine.apr import calculate_apr
from src.models.inputs import ArmScenario, ComparisonRequest, FixedScenario
from src.models.outputs import ComparisonResult, ErrorDetail, PricingResult

router = APIRouter()


def _price_fixed(scenario: FixedScenario) -> PricingResult:
    loan = scenario.loan_amount()
    fees = [f.amount for f in scenario.fee_schedule.fees]
    monthly = calculate_monthly_payment(loan, scenario.annual_rate, scenario.term_years)
    apr = calculate_apr(loan, monthly, scenario.term_years * 12, fees)
    total_interest = (monthly * scenario.term_years * 12 - loan).quantize(Decimal("0.01"))
    return PricingResult(
        scenario_id=scenario.scenario_id,
        loan_type="fixed",
        loan_amount=loan,
        monthly_payment=monthly,
        apr=apr,
        total_interest=total_interest,
        rate_type_label=f"Fixed {scenario.term_years}-year",
        parameters_summary={},
    )


def _price_arm(scenario: ArmScenario) -> PricingResult:
    loan = scenario.loan_amount()
    fees = [f.amount for f in scenario.fee_schedule.fees]
    monthly = calculate_arm_initial_payment(loan, scenario.initial_rate, scenario.term_years)
    apr = calculate_arm_apr(loan, monthly, scenario.term_years * 12, fees)
    total_interest = (monthly * scenario.term_years * 12 - loan).quantize(Decimal("0.01"))
    p = scenario.arm_params
    label = f"{p.fixed_period_years}/{p.adjustment_period_years} ARM {scenario.term_years}-year"
    return PricingResult(
        scenario_id=scenario.scenario_id,
        loan_type="arm",
        loan_amount=loan,
        monthly_payment=monthly,
        apr=apr,
        total_interest=total_interest,
        rate_type_label=label,
        parameters_summary={},
    )


def _price_raw(raw: Dict[str, Any]) -> PricingResult | ErrorDetail:
    scenario_id: str = raw.get("scenario_id") or str(uuid4())
    loan_type = raw.get("loan_type", "fixed")
    try:
        if loan_type == "fixed":
            return _price_fixed(FixedScenario.model_validate(raw))
        elif loan_type == "arm":
            return _price_arm(ArmScenario.model_validate(raw))
        else:
            return ErrorDetail(
                scenario_id=scenario_id,
                code="UNKNOWN_LOAN_TYPE",
                message=f"Unknown loan_type: {loan_type!r}",
                fields=["loan_type"],
            )
    except (ValidationError, Exception) as exc:
        return ErrorDetail(
            scenario_id=scenario_id,
            code="VALIDATION_ERROR",
            message=str(exc),
            fields=[],
        )


@router.post("/price/compare", response_model=ComparisonResult)
async def price_compare(request: ComparisonRequest) -> ComparisonResult:
    inputs_payload: Dict[str, Any] = {
        "comparison_id": request.comparison_id,
        "scenario_count": len(request.scenarios),
    }

    with audit_context("comparison", len(request.scenarios), inputs_payload) as record:
        results = [_price_raw(raw) for raw in request.scenarios]
        record["outputs_summary"] = {"scenario_count": len(request.scenarios)}

    return ComparisonResult(comparison_id=request.comparison_id, results=results)
