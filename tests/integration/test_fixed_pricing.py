"""Integration tests for full fixed-rate pricing pipeline."""
import json
from decimal import Decimal
from io import StringIO

import pytest

from src.engine.amortisation import calculate_monthly_payment
from src.engine.apr import calculate_apr
from src.models.inputs import FeeSchedule, FixedScenario


class TestFixedPricingPipeline:
    def test_loan_amount_derived_correctly(self):
        scenario = FixedScenario(
            home_price=Decimal("400000"),
            down_payment=Decimal("80000"),
            term_years=30,
            annual_rate=Decimal("6.5"),
        )
        assert scenario.loan_amount() == Decimal("320000")

    def test_payment_and_apr_pipeline(self):
        scenario = FixedScenario(
            home_price=Decimal("400000"),
            down_payment=Decimal("80000"),
            term_years=30,
            annual_rate=Decimal("6.5"),
        )
        loan = scenario.loan_amount()
        payment = calculate_monthly_payment(loan, scenario.annual_rate, scenario.term_years)
        apr = calculate_apr(loan, payment, scenario.term_years * 12, fees=[])
        assert payment == Decimal("2022.62")
        assert apr == Decimal("6.500")

    def test_percentage_down_payment_pipeline(self):
        scenario = FixedScenario(
            home_price=Decimal("400000"),
            down_payment="20%",
            term_years=30,
            annual_rate=Decimal("6.5"),
        )
        assert scenario.loan_amount() == Decimal("320000.00")
