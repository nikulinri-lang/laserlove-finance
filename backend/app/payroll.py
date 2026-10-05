from calendar import monthrange
from decimal import Decimal, ROUND_HALF_UP

Q = Decimal("0.01")

def money(v: Decimal) -> Decimal:
    return Decimal(v).quantize(Q, rounding=ROUND_HALF_UP)

def calculate_monthly_salary(gross: Decimal, ndfl_rate: Decimal = Decimal("0.13"), deductions: Decimal = Decimal("0")):
    ndfl = money(gross * ndfl_rate)
    net = money(gross - ndfl - deductions)
    return {"gross": money(gross), "ndfl": ndfl, "deductions": money(deductions), "net": net}

def working_days(year: int, month: int) -> int:
    # Temporary baseline. Production version will use an editable RF production calendar.
    days = monthrange(year, month)[1]
    return sum(1 for d in range(1, days + 1) if __import__("datetime").date(year, month, d).weekday() < 5)
