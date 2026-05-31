from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class PricingResult(BaseModel):
    scenario_id: str
    loan_type: str
    loan_amount: Decimal
    monthly_payment: Decimal
    apr: Decimal
    total_interest: Decimal
    rate_type_label: str
    parameters_summary: Dict[str, Any]


class ErrorDetail(BaseModel):
    scenario_id: Optional[str] = None
    error: bool = True
    code: str
    message: str
    fields: List[str] = []


PricingResultOrError = Union[PricingResult, ErrorDetail]


class ComparisonResult(BaseModel):
    comparison_id: str
    results: List[PricingResultOrError]


class AuditRecord(BaseModel):
    request_id: str
    timestamp: str
    loan_type: str
    scenario_count: int
    inputs_hash: str
    outputs_summary: Dict[str, Any]
    duration_ms: int
    error: Optional[str] = None
