"""Unit tests for ARM engine — must FAIL before T026 is implemented."""
from decimal import Decimal

import pytest

from src.engine.arm import calculate_arm_initial_payment, calculate_arm_apr
from src.models.inputs import ArmParameters


def _params(fp=5, ap=1, ic="2.00", pc="2.00", lc="5.00"):
    return ArmParameters(
        fixed_period_years=fp,
        adjustment_period_years=ap,
        initial_cap=Decimal(ic),
        periodic_cap=Decimal(pc),
        lifetime_cap=Decimal(lc),
    )


class TestArmInitialPayment:
    def test_5_1_arm_payment(self):
        result = calculate_arm_initial_payment(
            loan_amount=Decimal("280000"),
            initial_rate=Decimal("5.75"),
            term_years=30,
        )
        assert isinstance(result, Decimal)
        assert result > Decimal("0")

    def test_7_1_arm_payment(self):
        result = calculate_arm_initial_payment(
            loan_amount=Decimal("300000"),
            initial_rate=Decimal("6.00"),
            term_years=30,
        )
        assert isinstance(result, Decimal)
        assert result > Decimal("0")

    def test_payment_is_decimal(self):
        result = calculate_arm_initial_payment(
            loan_amount=Decimal("200000"),
            initial_rate=Decimal("5.00"),
            term_years=30,
        )
        assert isinstance(result, Decimal)

    def test_zero_rate_arm(self):
        result = calculate_arm_initial_payment(
            loan_amount=Decimal("120000"),
            initial_rate=Decimal("0"),
            term_years=10,
        )
        assert result == Decimal("1000.00")


class TestArmApr:
    def test_no_fees_arm_apr_equals_initial_rate(self):
        payment = calculate_arm_initial_payment(
            loan_amount=Decimal("280000"),
            initial_rate=Decimal("5.75"),
            term_years=30,
        )
        apr = calculate_arm_apr(
            loan_amount=Decimal("280000"),
            monthly_payment=payment,
            term_months=360,
            fees=[],
        )
        assert apr == Decimal("5.750")

    def test_with_fees_arm_apr_higher(self):
        payment = calculate_arm_initial_payment(
            loan_amount=Decimal("280000"),
            initial_rate=Decimal("5.75"),
            term_years=30,
        )
        apr_no_fees = calculate_arm_apr(Decimal("280000"), payment, 360, [])
        apr_with_fees = calculate_arm_apr(Decimal("280000"), payment, 360, [Decimal("1000")])
        assert apr_with_fees > apr_no_fees

    def test_result_is_decimal(self):
        payment = calculate_arm_initial_payment(Decimal("200000"), Decimal("5.0"), 30)
        result = calculate_arm_apr(Decimal("200000"), payment, 360, [])
        assert isinstance(result, Decimal)
