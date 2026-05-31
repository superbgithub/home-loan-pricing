from decimal import Decimal
from typing import List

from src.engine.amortisation import calculate_monthly_payment
from src.engine.apr import calculate_apr


def calculate_arm_initial_payment(
    loan_amount: Decimal,
    initial_rate: Decimal,
    term_years: int,
) -> Decimal:
    """
    Initial monthly P&I payment for an ARM loan.

    Uses the standard amortisation formula over the full term at the initial rate.
    This is the Regulation Z approach: APR is disclosed using the initial rate held
    constant for the entire term.
    """
    return calculate_monthly_payment(loan_amount, initial_rate, term_years)


def calculate_arm_apr(
    loan_amount: Decimal,
    monthly_payment: Decimal,
    term_months: int,
    fees: List[Decimal],
) -> Decimal:
    """
    APR for an ARM loan per Regulation Z initial-rate-held-constant assumption.

    Delegates to the same actuarial solver used for fixed-rate products.
    """
    return calculate_apr(loan_amount, monthly_payment, term_months, fees)
