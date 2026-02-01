from fastapi import FastAPI
from app.api.routes.auth import router as auth_router
from app.api.routes.analytics import router as analytics_router

app = FastAPI(title="Mini FactoryTwin Demo (Secure API -> Power BI)")

app.include_router(auth_router)
app.include_router(analytics_router)

@app.get("/health")
def health():
    return {"status": "ok"}
