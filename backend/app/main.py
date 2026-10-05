from __future__ import annotations
import json
from datetime import date, datetime
from decimal import Decimal
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import init_db, SessionLocal
from .models import Employee, SalaryHistory, PayrollRun, PayrollItem, Absence, AccountingEntry, AuditLog, UsnTaxPeriod, TaxPayment, UsnEntryClassification
from .payroll import calculate_monthly_salary\nfrom .tax import calculate_usn, quarter_number
from .exports import payroll_xlsx, inspect_1c_archive

app = FastAPI(title="Laser Love Finance", version="0.4.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def startup():
    init_db()


def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


class EmployeeIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    position: str = Field(default="Сотрудник", max_length=120)
    inn: str | None = None
    snils: str | None = None
    hire_date: date
    salary: Decimal = Field(gt=0)
    employment_rate: Decimal = Field(default=Decimal("1"), gt=0, le=1)
    vacation_days_total: Decimal = Decimal("28")
    insurance_years: Decimal = Decimal("0")
    bank_account: str | None = None


class PayrollRequest(BaseModel):
    employee_id: int | None = None
    gross: Decimal = Field(gt=0)
    prior_tax_base_ytd: Decimal = Decimal("0")
    deductions: Decimal = Decimal("0")
    contribution_rate: Decimal = Decimal("0.30")
    prior_contribution_base_ytd: Decimal = Decimal("0")


class AbsenceIn(BaseModel):
    employee_id: int
    kind: str
    start_date: date
    end_date: date
    days: int = Field(ge=1)
    amount: Decimal = Decimal("0")
    document_no: str | None = None


class AccountingIn(BaseModel):
    entry_date: date
    kind: str
    category: str
    description: str
    amount: Decimal = Field(gt=0)
    counterparty: str | None = None
    usn_recognized: bool = True
    usn_reason: str | None = None


@app.get("/health")
def health():
    return {"status": "ok", "service": "laserlove-finance", "version": "0.4.0"}


@app.get("/api/v1/dashboard")
def dashboard(session: Session = Depends(db)):
    employees = session.scalars(select(Employee).where(Employee.active.is_(True))).all()
    return {
        "employees": len(employees),
        "payroll_ready": all(e.salary and e.hire_date for e in employees),
        "active_salary": sum((Decimal(e.salary or 0) for e in employees), Decimal("0")),
        "vacation_days": sum((Decimal(e.vacation_days_total or 0) - Decimal(e.vacation_days_used or 0) for e in employees), Decimal("0")),
    }


@app.get("/api/v1/employees")
def employees(session: Session = Depends(db)):
    rows = session.scalars(select(Employee).order_by(Employee.active.desc(), Employee.full_name)).all()
    return [{
        "id": e.id, "full_name": e.full_name, "position": e.position,
        "hire_date": e.hire_date, "salary": e.salary, "employment_rate": e.employment_rate,
        "vacation_balance": Decimal(e.vacation_days_total or 0) - Decimal(e.vacation_days_used or 0),
        "active": e.active,
    } for e in rows]


@app.post("/api/v1/employees")
def create_employee(req: EmployeeIn, session: Session = Depends(db)):
    employee = Employee(**req.model_dump(), active=True)
    session.add(employee)
    session.flush()
    session.add(SalaryHistory(employee_id=employee.id, salary=employee.salary, effective_from=employee.hire_date, reason="Начальный оклад"))
    session.add(AuditLog(action="create", entity="employee", entity_id=employee.id, details=employee.full_name))
    session.commit()
    return {"id": employee.id, "status": "created"}


@app.post("/api/v1/payroll/calculate")
def calculate(req: PayrollRequest):
    return calculate_monthly_salary(
        req.gross, req.prior_tax_base_ytd, req.deductions, req.contribution_rate,
        req.prior_contribution_base_ytd
    )


@app.post("/api/v1/payroll/run")
def payroll_run(year: int, month: int, session: Session = Depends(db)):
    run = session.scalar(select(PayrollRun).where(PayrollRun.year == year, PayrollRun.month == month))
    if run and run.status == "closed":
        raise HTTPException(409, "Месяц закрыт. Сначала выполните переоткрытие.")
    if not run:
        run = PayrollRun(year=year, month=month, status="draft")
        session.add(run)
        session.flush()
    employees = session.scalars(select(Employee).where(Employee.active.is_(True))).all()
    results = []
    for e in employees:
        result = calculate_monthly_salary(Decimal(e.salary) * Decimal(e.employment_rate))
        item = session.scalar(select(PayrollItem).where(PayrollItem.payroll_id == run.id, PayrollItem.employee_id == e.id))
        values = dict(gross=result["gross"], ndfl=result["ndfl"], deductions=result["deductions"], net=result["net"],
                      employer_contributions=result["employer_contributions"], employer_cost=result["employer_cost"])
        if item:
            for k, v in values.items(): setattr(item, k, v)
        else:
            session.add(PayrollItem(payroll_id=run.id, employee_id=e.id, **values))
        results.append({"employee_id": e.id, "name": e.full_name, **result})
    session.add(AuditLog(action="calculate", entity="payroll_run", entity_id=run.id, details=f"{year}-{month:02d}"))
    session.commit()
    return {"run_id": run.id, "year": year, "month": month, "status": run.status, "items": results}


@app.post("/api/v1/payroll/{run_id}/close")
def close_payroll(run_id: int, session: Session = Depends(db)):
    run = session.get(PayrollRun, run_id)
    if not run:
        raise HTTPException(404, "Расчёт не найден")
    run.status = "closed"
    run.closed_at = datetime.utcnow()
    session.add(AuditLog(action="close", entity="payroll_run", entity_id=run_id))
    session.commit()
    return {"status": "closed", "run_id": run_id}


@app.get("/api/v1/absences")
def absences(session: Session = Depends(db)):
    return session.scalars(select(Absence).order_by(Absence.start_date.desc())).all()


@app.post("/api/v1/absences")
def create_absence(req: AbsenceIn, session: Session = Depends(db)):
    row = Absence(**req.model_dump())
    session.add(row)
    session.add(AuditLog(action="create", entity="absence", details=req.kind))
    session.commit()
    return {"status": "created", "id": row.id}


@app.get("/api/v1/accounting")
def accounting(session: Session = Depends(db)):
    return session.scalars(select(AccountingEntry).order_by(AccountingEntry.entry_date.desc(), AccountingEntry.id.desc())).all()


@app.post("/api/v1/accounting")
def create_accounting(req: AccountingIn, session: Session = Depends(db)):
    row = AccountingEntry(**req.model_dump())
    session.add(row)
    session.add(UsnEntryClassification(accounting_entry_id=row.id, recognized=req.usn_recognized, reason=req.usn_reason))
    session.add(AuditLog(action="create", entity="accounting_entry", details=req.description))
    session.commit()
    return {"status": "created", "id": row.id}


@app.get("/api/v1/taxes/usn")
def usn_tax(year: int = 2026, session: Session = Depends(db)):
    entries = session.scalars(select(AccountingEntry).where(AccountingEntry.entry_date >= date(year, 1, 1), AccountingEntry.entry_date < date(year + 1, 1, 1))).all()
    income = sum((Decimal(e.amount) for e in entries if e.kind == "income"), Decimal("0"))
    recognized = session.scalars(select(UsnEntryClassification).where(UsnEntryClassification.recognized.is_(True))).all()
    recognized_ids = {x.accounting_entry_id for x in recognized}
    expenses = sum((Decimal(e.amount) for e in entries if e.kind == "expense" and e.id in recognized_ids), Decimal("0"))
    payments = session.scalars(select(TaxPayment).where(TaxPayment.tax_type == "УСН", TaxPayment.period_year == year)).all()
    paid = sum((Decimal(p.amount) for p in payments), Decimal("0"))
    org_rate = Decimal("0.15")
    result = calculate_usn(year, income, expenses, org_rate, paid, is_year_end=False)
    return {k: str(v) if isinstance(v, Decimal) else v for k, v in result.__dict__.items()}


@app.post("/api/v1/taxes/usn/calculate")
def calculate_usn_tax(year: int = 2026, session: Session = Depends(db)):
    entries = session.scalars(select(AccountingEntry).where(AccountingEntry.entry_date >= date(year, 1, 1), AccountingEntry.entry_date < date(year + 1, 1, 1))).all()
    income = sum((Decimal(e.amount) for e in entries if e.kind == "income"), Decimal("0"))
    recognized = session.scalars(select(UsnEntryClassification).where(UsnEntryClassification.recognized.is_(True))).all()
    recognized_ids = {x.accounting_entry_id for x in recognized}
    expenses = sum((Decimal(e.amount) for e in entries if e.kind == "expense" and e.id in recognized_ids), Decimal("0"))
    payments = session.scalars(select(TaxPayment).where(TaxPayment.tax_type == "УСН", TaxPayment.period_year == year)).all()
    paid = sum((Decimal(p.amount) for p in payments), Decimal("0"))
    result = calculate_usn(year, income, expenses, Decimal("0.15"), paid, is_year_end=False)
    session.add(UsnTaxPeriod(year=year, quarter=4, income=result.income_ytd, recognized_expenses=result.expenses_ytd, tax_base=result.tax_base_ytd, calculated_tax=result.calculated_tax_ytd, minimum_tax=result.minimum_tax_ytd, target_tax=result.target_tax_ytd, paid_advances=result.paid_advances, payment_due=result.payment_due_ytd, status="draft"))
    session.add(AuditLog(action="calculate", entity="usn_tax", details=f"{year}: income={income}; expenses={expenses}"))
    session.commit()
    return {k: str(v) if isinstance(v, Decimal) else v for k, v in result.__dict__.items()}


@app.post("/api/v1/export/xlsx")
def export_xlsx(req: list[dict]):
    stream = payroll_xlsx(req)
    return StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=payroll.xlsx"})


@app.post("/api/v1/1c/inspect")
async def inspect_1c(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > 50 * 1024 * 1024:
        raise HTTPException(413, "Архив слишком большой. Максимум 50 МБ.")
    try:
        return inspect_1c_archive(data)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.post("/api/v1/1c/export")
def export_1c(year: int, month: int, session: Session = Depends(db)):
    run = session.scalar(select(PayrollRun).where(PayrollRun.year == year, PayrollRun.month == month))
    if not run or run.status != "closed":
        raise HTTPException(409, "Перед выгрузкой необходимо рассчитать и закрыть месяц.")
    items = session.scalars(select(PayrollItem).where(PayrollItem.payroll_id == run.id)).all()
    # Exchange envelope is deliberately explicit: it is a staging package, not a claim of
    # compatibility with an unknown 1C configuration. The exact target schema is configured later.
    import xml.etree.ElementTree as ET
    root = ET.Element("LaserLoveFinanceExchange", {"version": "1.0", "year": str(year), "month": str(month)})
    for item in items:
        ET.SubElement(root, "Payroll", {
            "employee_id": str(item.employee_id),
            "gross": str(item.gross),
            "ndfl": str(item.ndfl),
            "net": str(item.net),
            "employer_contributions": str(item.employer_contributions),
        })
    xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return StreamingResponse(iter([xml]), media_type="application/xml",
        headers={"Content-Disposition": f"attachment; filename=laserlove-payroll-{year}-{month:02d}.xml"})
