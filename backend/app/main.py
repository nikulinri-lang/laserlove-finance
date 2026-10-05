from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from decimal import Decimal
from .db import init_db
from .payroll import calculate_monthly_salary
from .exports import payroll_xlsx, inspect_1c_archive

app = FastAPI(title="Laser Love Finance", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    init_db()

class PayrollRequest(BaseModel):
    gross: Decimal
    ndfl_rate: Decimal = Decimal("0.13")
    deductions: Decimal = Decimal("0")

@app.get("/health")
def health():
    return {"status":"ok","service":"laserlove-finance","version":"0.2.0"}

@app.post("/api/v1/payroll/calculate")
def calculate(req: PayrollRequest):
    return calculate_monthly_salary(req.gross, req.ndfl_rate, req.deductions)

@app.post("/api/v1/export/xlsx")
def export_xlsx(req: list[dict]):
    stream = payroll_xlsx(req)
    return StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=payroll.xlsx"})

@app.post("/api/v1/1c/inspect")
async def inspect_1c(file: UploadFile = File(...)):
    data = await file.read()
    try:
        return inspect_1c_archive(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
