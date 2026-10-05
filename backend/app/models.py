from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, Numeric, String, Boolean, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): pass

class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200))
    position: Mapped[str] = mapped_column(String(120))
    inn: Mapped[str | None] = mapped_column(String(12), nullable=True)
    snils: Mapped[str | None] = mapped_column(String(20), nullable=True)
    hire_date: Mapped[date] = mapped_column(Date)
    fire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    salary: Mapped[Decimal] = mapped_column(Numeric(12,2))
    employment_rate: Mapped[Decimal] = mapped_column(Numeric(5,2), default=Decimal("1.00"))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    bank_account: Mapped[str | None] = mapped_column(String(34), nullable=True)

class PayrollRun(Base):
    __tablename__ = "payroll_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int]
    month: Mapped[int]
    status: Mapped[str] = mapped_column(String(30), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PayrollItem(Base):
    __tablename__ = "payroll_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    payroll_id: Mapped[int]
    employee_id: Mapped[int]
    gross: Mapped[Decimal] = mapped_column(Numeric(12,2))
    ndfl: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)
    deductions: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)
    net: Mapped[Decimal] = mapped_column(Numeric(12,2))
    employer_contributions: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

class Absence(Base):
    __tablename__ = "absences"
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int]
    kind: Mapped[str] = mapped_column(String(30))
    start_date: Mapped[date]
    end_date: Mapped[date]
    days: Mapped[int]
    amount: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)
    document_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
