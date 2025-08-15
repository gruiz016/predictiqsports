# api/app/stripe_client.py
import stripe
from .config import settings

if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

try:
    stripe.default_http_client = stripe.http_client.new_default_http_client(timeout=10)
except Exception:
    pass

def ensure_configured():
    if not settings.STRIPE_SECRET_KEY:
        raise RuntimeError("Stripe not configured: STRIPE_SECRET_KEY missing")
    if not (settings.STRIPE_PRICE_MONTHLY or settings.STRIPE_PRICE_QUARTERLY or settings.STRIPE_PRICE_YEARLY):
        raise RuntimeError("Stripe price IDs missing; set STRIPE_PRICE_MONTHLY/QUARTERLY/YEARLY")

def get_price_id(plan: str) -> str:
    m = {
        "monthly": settings.STRIPE_PRICE_MONTHLY,
        "quarterly": settings.STRIPE_PRICE_QUARTERLY,
        "yearly": settings.STRIPE_PRICE_YEARLY,
    }
    pid = m.get(plan)
    if not pid:
        raise ValueError("Invalid plan")
    return pid
