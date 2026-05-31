from __future__ import annotations

import re
from decimal import Decimal
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class Fee(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    amount: Decimal = Field(gt=Decimal("0"))


class FeeSchedule(BaseModel):
    fees: List[Fee] = Field(default_factory=list)


_PERCENTAGE_RE = re.compile(r"^\d+(\.\d+)?%$")


def _parse_money_or_pct(value: object) -> object:
    """Convert string inputs: percentage strings kept as str, others coerced to Decimal."""
    if isinstance(value, str):
        if _PERCENTAGE_RE.match(value.strip()):
            return value.strip()
        return Decimal(value)
    return value


class FixedScenario(BaseModel):
    loan_type: Literal["fixed"] = "fixed"
    scenario_id: str = Field(default_factory=lambda: str(uuid4()))
    home_price: Decimal = Field(gt=Decimal("0"))
    down_payment: Union[Decimal, str]
    term_years: int = Field(gt=0, le=50)
    annual_rate: Decimal = Field(ge=Decimal("0"), le=Decimal("30"))
    fee_schedule: FeeSchedule = Field(default_factory=FeeSchedule)

    @field_validator("down_payment", mode="before")
    @classmethod
    def parse_down_payment(cls, v: object) -> object:
        return _parse_money_or_pct(v)

    @model_validator(mode="after")
    def validate_loan_amount(self) -> "FixedScenario":
        dp = _resolve_down_payment(self.down_payment, self.home_price)
        if dp < Decimal("0"):
            raise ValueError("down_payment must be >= 0")
        if dp >= self.home_price:
            raise ValueError("down_payment must be less than home_price")
        return self

    def loan_amount(self) -> Decimal:
        return self.home_price - _resolve_down_payment(self.down_payment, self.home_price)


class ArmParameters(BaseModel):
    fixed_period_years: int = Field(ge=1)
    adjustment_period_years: int = Field(ge=1)
    initial_cap: Decimal = Field(ge=Decimal("0"))
    periodic_cap: Decimal = Field(gt=Decimal("0"))
    lifetime_cap: Decimal = Field(gt=Decimal("0"))

    @model_validator(mode="after")
    def validate_caps(self) -> "ArmParameters":
        if self.periodic_cap > self.lifetime_cap:
            raise ValueError(
                "periodic_cap must be <= lifetime_cap (PERIODIC_CAP_EXCEEDS_LIFETIME)"
            )
        return self


class ArmScenario(BaseModel):
    loan_type: Literal["arm"] = "arm"
    scenario_id: str = Field(default_factory=lambda: str(uuid4()))
    home_price: Decimal = Field(gt=Decimal("0"))
    down_payment: Union[Decimal, str]
    term_years: int = Field(gt=0, le=50)
    initial_rate: Decimal = Field(ge=Decimal("0"), le=Decimal("30"))
    arm_params: ArmParameters
    fee_schedule: FeeSchedule = Field(default_factory=FeeSchedule)

    @field_validator("down_payment", mode="before")
    @classmethod
    def parse_down_payment(cls, v: object) -> object:
        return _parse_money_or_pct(v)

    @model_validator(mode="after")
    def validate_arm_scenario(self) -> "ArmScenario":
        dp = _resolve_down_payment(self.down_payment, self.home_price)
        if dp < Decimal("0"):
            raise ValueError("down_payment must be >= 0")
        if dp >= self.home_price:
            raise ValueError("down_payment must be less than home_price")
        if self.arm_params.fixed_period_years >= self.term_years:
            raise ValueError(
                "fixed_period_years must be < term_years (FIXED_PERIOD_EXCEEDS_TERM)"
            )
        max_rate = self.initial_rate + self.arm_params.lifetime_cap
        if max_rate > Decimal("30"):
            raise ValueError(
                "initial_rate + lifetime_cap must be <= 30 (MAX_RATE_EXCEEDS_CEILING)"
            )
        return self

    def loan_amount(self) -> Decimal:
        return self.home_price - _resolve_down_payment(self.down_payment, self.home_price)


class ComparisonRequest(BaseModel):
    comparison_id: str = Field(default_factory=lambda: str(uuid4()))
    # Raw dicts so the route can validate each scenario independently and return
    # per-scenario ErrorDetail instead of rejecting the whole request on one bad input.
    scenarios: List[Dict[str, Any]] = Field(min_length=1, max_length=5)


def _resolve_down_payment(down_payment: Union[Decimal, str], home_price: Decimal) -> Decimal:
    """Convert percentage string or Decimal to a dollar Decimal amount."""
    if isinstance(down_payment, str):
        pct = Decimal(down_payment.rstrip("%")) / Decimal("100")
        return (home_price * pct).quantize(Decimal("0.01"))
    return down_payment
