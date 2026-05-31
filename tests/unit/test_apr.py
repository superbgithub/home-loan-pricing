"""Unit tests for APR solver — must FAIL before T017 is implemented."""
from decimal import Decimal

import pytest

from src.engine.apr import calculate_apr


class TestCalculateApr:
    def test_no_fees_apr_equals_rate(self):
        # With no fees, APR should equal the stated rate
        monthly = Decimal("2022.62")
        result = calculate_apr(
            loan_amount=Decimal("320000"),
            monthly_payment=monthly,
            term_months=360,
            fees=[],
        )
        assert result == Decimal("6.500")

    def test_with_fees_apr_higher_than_rate(self):
        # Adding $1500 origination fee raises APR above 6.5%
        monthly = Decimal("2022.62")
        result = calculate_apr(
            loan_amount=Decimal("320000"),
            monthly_payment=monthly,
            term_months=360,
            fees=[Decimal("1500")],
        )
        assert result > Decimal("6.500")

    def test_result_is_decimal(self):
        result = calculate_apr(
            loan_amount=Decimal("200000"),
            monthly_payment=Decimal("1330.60"),
            term_months=240,
            fees=[],
        )
        assert isinstance(result, Decimal)

    def test_apr_rounded_to_three_decimals(self):
        result = calculate_apr(
            loan_amount=Decimal("320000"),
            monthly_payment=Decimal("2022.65"),
            term_months=360,
            fees=[],
        )
        # Should have at most 3 decimal places
        assert result == result.quantize(Decimal("0.001"))
