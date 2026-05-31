"""Validation tests for input boundary rules."""
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.models.inputs import ArmParameters, ArmScenario, FixedScenario


class TestFixedScenarioValidation:
    def _valid(self, **overrides):
        data = {
            "home_price": "400000.00",
            "down_payment": "80000.00",
            "term_years": 30,
            "annual_rate": "6.50",
        }
        data.update(overrides)
        return data

    def test_valid_scenario_accepted(self):
        s = FixedScenario(**self._valid())
        assert s.loan_amount() == Decimal("320000.00")

    def test_negative_rate_rejected(self):
        with pytest.raises(ValidationError):
            FixedScenario(**self._valid(annual_rate="-1"))

    def test_rate_above_30_rejected(self):
        with pytest.raises(ValidationError):
            FixedScenario(**self._valid(annual_rate="31"))

    def test_zero_term_rejected(self):
        with pytest.raises(ValidationError):
            FixedScenario(**self._valid(term_years=0))

    def test_down_payment_equals_home_price_rejected(self):
        with pytest.raises(ValidationError):
            FixedScenario(**self._valid(down_payment="400000.00"))

    def test_down_payment_exceeds_home_price_rejected(self):
        with pytest.raises(ValidationError):
            FixedScenario(**self._valid(down_payment="500000.00"))

    def test_percentage_down_payment_accepted(self):
        s = FixedScenario(**self._valid(down_payment="20%"))
        assert s.loan_amount() == Decimal("320000.00")

    def test_zero_rate_accepted(self):
        s = FixedScenario(**self._valid(annual_rate="0"))
        assert s.annual_rate == Decimal("0")


class TestArmScenarioValidation:
    def _valid_arm(self, **overrides):
        data = {
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
        data.update(overrides)
        return data

    def test_valid_arm_accepted(self):
        s = ArmScenario(**self._valid_arm())
        assert s.loan_type == "arm"

    def test_periodic_cap_exceeds_lifetime_rejected(self):
        with pytest.raises(ValidationError, match="PERIODIC_CAP_EXCEEDS_LIFETIME"):
            ArmScenario(
                **self._valid_arm(
                    arm_params={
                        "fixed_period_years": 5,
                        "adjustment_period_years": 1,
                        "initial_cap": "2.00",
                        "periodic_cap": "6.00",
                        "lifetime_cap": "5.00",
                    }
                )
            )

    def test_fixed_period_exceeds_term_rejected(self):
        with pytest.raises(ValidationError, match="FIXED_PERIOD_EXCEEDS_TERM"):
            ArmScenario(**self._valid_arm(term_years=5))

    def test_max_rate_ceiling_rejected(self):
        with pytest.raises(ValidationError, match="MAX_RATE_EXCEEDS_CEILING"):
            ArmScenario(
                **self._valid_arm(
                    initial_rate="29.00",
                    arm_params={
                        "fixed_period_years": 5,
                        "adjustment_period_years": 1,
                        "initial_cap": "2.00",
                        "periodic_cap": "2.00",
                        "lifetime_cap": "5.00",
                    },
                )
            )
