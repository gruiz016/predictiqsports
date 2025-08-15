# api/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers_auth import router as auth_router
from .routers_billing import router as billing_router, webhooks as billing_webhooks
from .routers_predictions import router as predictions_router
from .routers_parlay import router as parlay_router

app = FastAPI(title="PredictIQ Sports API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(billing_router)
app.include_router(billing_webhooks)
app.include_router(predictions_router)
app.include_router(parlay_router)

@app.get("/healthz")
async def healthz():
    return {"ok": True, "version": "0.3.0"}
