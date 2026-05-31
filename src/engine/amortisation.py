from decimal import Decimal, ROUND_HALF_UP, localcontext


def calculate_monthly_payment(
    principal: Decimal,
    annual_rate: Decimal,
    term_years: int,
) -> Decimal:
    """Return the monthly principal-and-interest payment rounded to cents."""
    n = term_years * 12
    if annual_rate == Decimal("0"):
        raw = principal / Decimal(n)
    else:
        # Use 50-digit precision for intermediate calculations so that
        # (1 + r)^360 accumulates no meaningful rounding error.
        with localcontext() as ctx:
            ctx.prec = 50
            r = annual_rate / Decimal("1200")
            factor = (1 + r) ** n
            raw = principal * r * factor / (factor - 1)
    return raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
