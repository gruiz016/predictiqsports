# api/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import healthcheck
from .routers_predictions import router as predictions_router
from .routers_auth import router as auth_router
from .routers_billing import router as billing_router, webhooks as stripe_webhooks
import stripe
if settings.STRIPE_SECRET_KEY: stripe.api_key=settings.STRIPE_SECRET_KEY
app=FastAPI(title="Sports Prediction & Parlay API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
@app.get("/health")
async def health(): await healthcheck(); return {"ok":True}
app.include_router(auth_router)
app.include_router(predictions_router)
app.include_router(billing_router)
app.include_router(stripe_webhooks)
