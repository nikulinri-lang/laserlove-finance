from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

Q = Decimal("0.01")

def money(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(Q, rounding=ROUND_HALF_UP)

@dataclass(frozen=True)
class UsnResult:
    year: int
    income_ytd: Decimal
    expenses_ytd: Decimal
    tax_base_ytd: Decimal
    calculated_tax_ytd: Decimal
    minimum_tax_ytd: Decimal
    target_tax_ytd: Decimal
    paid_advances: Decimal
    payment_due_ytd: Decimal

def calculate_usn(year: int, income_ytd: Decimal, expenses_ytd: Decimal, rate: Decimal = Decimal("0.15"), paid_advances: Decimal = Decimal("0"), is_year_end: bool = False) -> UsnResult:
    income = money(max(Decimal("0"), income_ytd))
    expenses = money(max(Decimal("0"), expenses_ytd))
    rate = Decimal(str(rate))
    if rate <= 0 or rate > 1:
        raise ValueError("Ставка УСН должна быть больше 0 и не превышать 100%.")
    base = money(max(Decimal("0"), income - expenses))
    calculated = money(base * rate)
    minimum = money(income * Decimal("0.01"))
    target = max(calculated, minimum) if is_year_end else calculated
    paid = money(max(Decimal("0"), paid_advances))
    due = money(max(Decimal("0"), target - paid))
    return UsnResult(year, income, expenses, base, calculated, minimum, target, paid, due)

def quarter_number(month: int) -> int:
    if month < 1 or month > 12:
        raise ValueError("Месяц должен быть от 1 до 12.")
    return (month - 1) // 3 + 1