from decimal import Decimal
from app.tax import calculate_usn


def test_usn_normal():
    r = calculate_usn(2026, Decimal("25000000"), Decimal("24000000"), Decimal("0.15"), is_year_end=True)
    assert r.tax_base_ytd == Decimal("1000000.00")
    assert r.calculated_tax_ytd == Decimal("150000.00")
    assert r.minimum_tax_ytd == Decimal("250000.00")
    assert r.target_tax_ytd == Decimal("250000.00")


def test_usn_advance_uses_cumulative_base():
    r = calculate_usn(2026, Decimal("4540000"), Decimal("3730000"), Decimal("0.15"), Decimal("82500"))
    assert r.calculated_tax_ytd == Decimal("121500.00")
    assert r.payment_due_ytd == Decimal("39000.00")


def test_usn_no_negative_base():
    r = calculate_usn(2026, Decimal("100000"), Decimal("150000"), Decimal("0.15"))
    assert r.tax_base_ytd == Decimal("0.00")
    assert r.calculated_tax_ytd == Decimal("0.00")
