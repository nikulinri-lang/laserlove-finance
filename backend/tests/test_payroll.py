from decimal import Decimal
from app.payroll import progressive_ndfl, monthly_ndfl, sick_pay, vacation_pay

def test_ndfl_2026_first_bracket():
    assert progressive_ndfl(Decimal("2400000")) == Decimal("312000.00")

def test_ndfl_progression():
    assert progressive_ndfl(Decimal("5000000")) == Decimal("702000.00")
    assert progressive_ndfl(Decimal("6000000")) == Decimal("882000.00")

def test_monthly_ndfl_is_incremental():
    tax, ytd = monthly_ndfl(Decimal("100000"), Decimal("2400000"))
    assert tax == Decimal("15000.00")
    assert ytd == Decimal("327000.00")

def test_vacation_pay():
    assert vacation_pay(Decimal("2000"), 14) == Decimal("28000.00")

def test_sick_pay():
    assert sick_pay(Decimal("2000"), 10, Decimal("10")) == Decimal("20000.00")
    assert sick_pay(Decimal("2000"), 10, Decimal("6")) == Decimal("16000.00")
