from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, Numeric, String, Boolean, Text, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), default="Laser Love")
    inn: Mapped[str | None] = mapped_column(String(12), nullable=True)
    kpp: Mapped[str | None] = mapped_column(String(9), nullable=True)
    ogrn: Mapped[str | None] = mapped_column(String(15), nullable=True)
    tax_system: Mapped[str] = mapped_column(String(40), default="УСН доходы минус расходы")
    usn_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0.15"))
    vat_mode: Mapped[str] = mapped_column(String(40), default="освобождение")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200))
    position: Mapped[str] = mapped_column(String(120))
    inn: Mapped[str | None] = mapped_column(String(12), nullable=True)
    snils: Mapped[str | None] = mapped_column(String(20), nullable=True)
    hire_date: Mapped[date] = mapped_column(Date)
    fire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    salary: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    employment_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("1.00"))
    vacation_days_total: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("28"))
    vacation_days_used: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("0"))
    insurance_years: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    bank_account: Mapped[str | None] = mapped_column(String(34), nullable=True)


class SalaryHistory(Base):
    __tablename__ = "salary_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    salary: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    effective_from: Mapped[date] = mapped_column(Date)
    reason: Mapped[str | None] = mapped_column(String(250), nullable=True)


class PayrollRun(Base):
    __tablename__ = "payroll_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int]
    month: Mapped[int]
    status: Mapped[str] = mapped_column(String(30), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class PayrollItem(Base):
    __tablename__ = "payroll_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    payroll_id: Mapped[int] = mapped_column(ForeignKey("payroll_runs.id"))
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    gross: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    ndfl: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    deductions: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    net: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    employer_contributions: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    employer_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Absence(Base):
    __tablename__ = "absences"
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    kind: Mapped[str] = mapped_column(String(30))
    start_date: Mapped[date]
    end_date: Mapped[date]
    days: Mapped[int]
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    document_no: Mapped[str | None] = mapped_column(String(100), nullable=True)


class AccountingEntry(Base):
    __tablename__ = "accounting_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    entry_date: Mapped[date] = mapped_column(Date)
    kind: Mapped[str] = mapped_column(String(30))  # income / expense / payment
    category: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(500))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    counterparty: Mapped[str | None] = mapped_column(String(200), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(80))
    entity: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExchangePackage(Base):
    __tablename__ = "exchange_packages"
    id: Mapped[int] = mapped_column(primary_key=True)
    direction: Mapped[str] = mapped_column(String(20))  # import/export
    format: Mapped[str] = mapped_column(String(50), default="1c-xml")
    filename: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(30), default="inspected")
    manifest: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
