"""Unit tests for amortisation formula — must FAIL before T016 is implemented."""
from decimal import Decimal

import pytest

from src.engine.amortisation import calculate_monthly_payment


class TestCalculateMonthlyPayment:
    def test_standard_30yr(self):
        # $320,000 at 6.5% for 30 years → $2,022.62 (exact amortisation formula)
        result = calculate_monthly_payment(
            principal=Decimal("320000"),
            annual_rate=Decimal("6.5"),
            term_years=30,
        )
        assert result == Decimal("2022.62")

    def test_standard_15yr(self):
        # $320,000 at 6.0% for 15 years → $2,700.34 (exact amortisation formula)
        result = calculate_monthly_payment(
            principal=Decimal("320000"),
            annual_rate=Decimal("6.0"),
            term_years=15,
        )
        assert result == Decimal("2700.34")

    def test_zero_interest(self):
        # Zero-rate: monthly = principal / n
        result = calculate_monthly_payment(
            principal=Decimal("120000"),
            annual_rate=Decimal("0"),
            term_years=10,
        )
        assert result == Decimal("1000.00")

    def test_result_is_decimal(self):
        result = calculate_monthly_payment(
            principal=Decimal("200000"),
            annual_rate=Decimal("5.0"),
            term_years=20,
        )
        assert isinstance(result, Decimal)

    def test_no_float_in_output(self):
        result = calculate_monthly_payment(
            principal=Decimal("200000"),
            annual_rate=Decimal("5.0"),
            term_years=20,
        )
        assert "E" not in str(result)  # no scientific notation

    def test_10yr_term(self):
        result = calculate_monthly_payment(
            principal=Decimal("100000"),
            annual_rate=Decimal("7.0"),
            term_years=10,
        )
        assert isinstance(result, Decimal)
        assert result > Decimal("0")
