from decimal import Decimal, ROUND_HALF_UP
from calendar import monthrange
from datetime import date
Q=Decimal("0.01")
def money(v): return Decimal(v).quantize(Q,rounding=ROUND_HALF_UP)
def calculate_monthly_salary(gross,ndfl_rate=Decimal("0.13"),deductions=Decimal("0")):
    gross=money(gross); ndfl=money(gross*ndfl_rate); deductions=money(deductions)
    return {"gross":gross,"ndfl":ndfl,"deductions":deductions,"net":money(gross-ndfl-deductions)}
def working_days(year,month):
    return sum(1 for d in range(1,monthrange(year,month)[1]+1) if date(year,month,d).weekday()<5)
