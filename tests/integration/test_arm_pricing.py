"""Integration tests for ARM pricing pipeline."""
from decimal import Decimal

import pytest

from src.engine.arm import calculate_arm_initial_payment, calculate_arm_apr
from src.models.inputs import ArmParameters, ArmScenario


class TestArmPricingPipeline:
    def test_arm_loan_amount_derived_correctly(self):
        scenario = ArmScenario(
            home_price=Decimal("350000"),
            down_payment=Decimal("70000"),
            term_years=30,
            initial_rate=Decimal("5.75"),
            arm_params=ArmParameters(
                fixed_period_years=5,
                adjustment_period_years=1,
                initial_cap=Decimal("2"),
                periodic_cap=Decimal("2"),
                lifetime_cap=Decimal("5"),
            ),
        )
        assert scenario.loan_amount() == Decimal("280000")

    def test_arm_payment_pipeline(self):
        scenario = ArmScenario(
            home_price=Decimal("350000"),
            down_payment=Decimal("70000"),
            term_years=30,
            initial_rate=Decimal("5.75"),
            arm_params=ArmParameters(
                fixed_period_years=5,
                adjustment_period_years=1,
                initial_cap=Decimal("2"),
                periodic_cap=Decimal("2"),
                lifetime_cap=Decimal("5"),
            ),
        )
        loan = scenario.loan_amount()
        payment = calculate_arm_initial_payment(loan, scenario.initial_rate, scenario.term_years)
        apr = calculate_arm_apr(loan, payment, scenario.term_years * 12, [])
        assert isinstance(payment, Decimal)
        assert apr == Decimal("5.750")
