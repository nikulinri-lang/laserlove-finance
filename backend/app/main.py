from fastapi import FastAPI

app = FastAPI(
    title="Laser Love Finance",
    version="0.1.0",
    description="Зарплата, кадры и помощник бухгалтера для Laser Love.",
)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "laserlove-finance"}

@app.get("/api/v1")
def api_root() -> dict[str, str]:
    return {"name": "Laser Love Finance", "version": "0.1.0"}
