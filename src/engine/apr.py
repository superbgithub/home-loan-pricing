from decimal import Decimal, ROUND_HALF_UP
from typing import List


class APRConvergenceError(Exception):
    pass


def calculate_apr(
    loan_amount: Decimal,
    monthly_payment: Decimal,
    term_months: int,
    fees: List[Decimal],
) -> Decimal:
    """
    Regulation Z actuarial APR (12 CFR Part 1026 Appendix J).

    The APR is the annual rate r such that:
        loan_amount - sum(fees) = sum(monthly_payment / (1 + r/12)^t, t=1..n)

    Solved via Newton-Raphson in Decimal arithmetic.
    Result rounded to 3 decimal places (Reg Z convention).
    """
    amount_financed = loan_amount - sum(fees, Decimal("0"))

    # Initial guess: stated annual rate approximation
    guess = Decimal("0.065")  # 6.5% as starting point

    for _ in range(200):
        monthly_r = guess / Decimal("12")
        pv, dpv = _pv_and_derivative(monthly_payment, monthly_r, term_months)
        f = pv - amount_financed
        # Derivative of PV w.r.t. annual rate = derivative w.r.t. monthly_r / 12
        df = dpv / Decimal("12")
        if df == Decimal("0"):
            break
        step = f / df
        guess = guess - step
        if abs(step) < Decimal("0.0000001"):
            break
    else:
        raise APRConvergenceError("APR solver did not converge")

    annual_pct = guess * Decimal("100")
    return annual_pct.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def _pv_and_derivative(
    payment: Decimal, monthly_r: Decimal, n: int
) -> tuple[Decimal, Decimal]:
    """Return (PV, dPV/d(monthly_r)) for an annuity."""
    pv = Decimal("0")
    dpv = Decimal("0")
    one = Decimal("1")
    for t in range(1, n + 1):
        discount = (one + monthly_r) ** t
        pv += payment / discount
        dpv += Decimal(-t) * payment / ((one + monthly_r) ** (t + 1))
    return pv, dpv
