from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
from calendar import monthrange
from datetime import date
from typing import Iterable

Q = Decimal("0.01")
D13 = Decimal("0.13")
NDFL_BRACKETS = (
    (Decimal("2400000"), Decimal("0.13")),
    (Decimal("5000000"), Decimal("0.15")),
    (Decimal("20000000"), Decimal("0.18")),
    (Decimal("50000000"), Decimal("0.20")),
    (None, Decimal("0.22")),
)
DEFAULT_SOCIAL_BASE_LIMIT_2026 = Decimal("2979000")
DEFAULT_SOCIAL_RATE = Decimal("0.30")


def money(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(Q, rounding=ROUND_HALF_UP)


def progressive_ndfl(total_base_ytd: Decimal) -> Decimal:
    remaining = max(Decimal("0"), money(total_base_ytd))
    previous = Decimal("0")
    tax = Decimal("0")
    for upper, rate in NDFL_BRACKETS:
        if upper is None:
            taxable = remaining
        else:
            taxable = max(Decimal("0"), min(remaining, upper - previous))
        tax += taxable * rate
        if upper is None or remaining <= upper:
            break
        previous = upper
    return money(tax)


def monthly_ndfl(current_base: Decimal, prior_base_ytd: Decimal = Decimal("0")) -> tuple[Decimal, Decimal]:
    current_base = max(Decimal("0"), money(current_base))
    prior_base_ytd = max(Decimal("0"), money(prior_base_ytd))
    total_tax = progressive_ndfl(prior_base_ytd + current_base)
    prior_tax = progressive_ndfl(prior_base_ytd)
    return money(total_tax - prior_tax), total_tax


def social_contributions(current_base: Decimal, prior_base_ytd: Decimal = Decimal("0"),
                         rate: Decimal = DEFAULT_SOCIAL_RATE,
                         base_limit: Decimal = DEFAULT_SOCIAL_BASE_LIMIT_2026) -> Decimal:
    current_base = max(Decimal("0"), money(current_base))
    prior_base_ytd = max(Decimal("0"), money(prior_base_ytd))
    taxable_before = min(current_base, max(Decimal("0"), base_limit - prior_base_ytd))
    taxable_after = max(Decimal("0"), current_base - taxable_before)
    # Default is the general unified rate. Special MСП/other rates are configurable later.
    return money(taxable_before * rate + taxable_after * rate)


def working_days(year: int, month: int, holidays: Iterable[date] = ()) -> int:
    excluded = {d for d in holidays if d.year == year and d.month == month}
    return sum(
        1 for day in range(1, monthrange(year, month)[1] + 1)
        if date(year, month, day).weekday() < 5 and date(year, month, day) not in excluded
    )


def vacation_pay(avg_daily: Decimal, calendar_days: int) -> Decimal:
    return money(max(Decimal("0"), avg_daily) * max(0, calendar_days))


def sick_pay(avg_daily: Decimal, days: int, insurance_years: Decimal) -> Decimal:
    if insurance_years < 5:
        rate = Decimal("0.60")
    elif insurance_years < 8:
        rate = Decimal("0.80")
    else:
        rate = Decimal("1.00")
    return money(max(Decimal("0"), avg_daily) * max(0, days) * rate)


def calculate_monthly_salary(
    gross: Decimal,
    prior_tax_base_ytd: Decimal = Decimal("0"),
    deductions: Decimal = Decimal("0"),
    contribution_rate: Decimal = DEFAULT_SOCIAL_RATE,
    prior_contribution_base_ytd: Decimal = Decimal("0"),
    contribution_base_limit: Decimal = DEFAULT_SOCIAL_BASE_LIMIT_2026,
) -> dict:
    gross = money(gross)
    deductions = money(deductions)
    tax_base = max(Decimal("0"), gross - deductions)
    ndfl, ndfl_ytd = monthly_ndfl(tax_base, prior_tax_base_ytd)
    contributions = social_contributions(
        gross, prior_contribution_base_ytd, contribution_rate, contribution_base_limit
    )
    return {
        "gross": gross,
        "tax_base": tax_base,
        "ndfl": ndfl,
        "deductions": deductions,
        "net": money(gross - ndfl - deductions),
        "employer_contributions": contributions,
        "employer_cost": money(gross + contributions),
        "ndfl_ytd": ndfl_ytd,
        "tax_base_ytd": money(prior_tax_base_ytd + tax_base),
        "contribution_base_ytd": money(prior_contribution_base_ytd + gross),
    }
