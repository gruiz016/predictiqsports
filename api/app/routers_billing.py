# api/app/routers_billing.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone
import stripe, uuid

from .auth import get_db, require_auth
from .config import settings
from .models import Subscription
from .stripe_client import ensure_configured, get_price_id

router = APIRouter(prefix="/v1/billing", tags=["billing"])

# ---------- helpers ----------
def _map_plan(interval: str | None, interval_count: int | None) -> str | None:
    if not interval:
        return None
    try:
        cnt = int(interval_count) if interval_count is not None else 1
    except Exception:
        cnt = 1
    if interval == "month" and cnt == 1:
        return "monthly"
    if interval == "month" and cnt == 3:
        return "quarterly"
    if interval == "year" and cnt == 1:
        return "yearly"
    return None

async def _upsert_sub(db: AsyncSession, user_id: str, stripe_cust: str | None, stripe_sub: str | None, status_val: str | None, current_period_end: int | None, plan_interval: str | None, plan_count: int | None):
    cpe_dt = datetime.fromtimestamp(current_period_end, tz=timezone.utc) if current_period_end else None
    plan = _map_plan(plan_interval, plan_count)
    existing = (await db.execute(select(Subscription).where(Subscription.user_id == uuid.UUID(user_id)))).scalar_one_or_none()
    now = datetime.now(tz=timezone.utc)
    values = dict(
        stripe_customer_id=stripe_cust,
        stripe_sub_id=stripe_sub,
        status=status_val,
        current_period_end=cpe_dt,
        plan=plan,
        updated_at=now,
    )
    if existing:
        await db.execute(update(Subscription).where(Subscription.user_id == uuid.UUID(user_id)).values(**values))
    else:
        db.add(Subscription(id=uuid.uuid4(), user_id=uuid.UUID(user_id), **values))
    await db.commit()

def _extract_plan_from_subscription(sub: dict) -> tuple[str | None, int | None]:
    items = (sub.get("items") or {}).get("data") or []
    if not items:
        return (None, None)
    item = items[0] or {}
    price = item.get("price") or {}
    recurring = price.get("recurring") or {}
    interval = recurring.get("interval")
    interval_count = recurring.get("interval_count")
    if interval:
        return (interval, interval_count)
    plan = item.get("plan") or {}
    return (plan.get("interval"), plan.get("interval_count"))

def _auto_get_or_create_portal_configuration() -> str | None:
    """Return a configuration ID to use for Customer Portal.
    Priority:
      1) env STRIPE_PORTAL_CONFIGURATION_ID (if present)
      2) first existing active configuration
      3) create a minimal configuration on the fly
    """
    ensure_configured()
    env_id = getattr(settings, "STRIPE_PORTAL_CONFIGURATION_ID", "") or ""
    if env_id:
        return env_id
    try:
        res = stripe.billing_portal.Configuration.list(limit=10)
        for c in res.get("data", []):
            if c.get("active"):
                return c.get("id")
        created = stripe.billing_portal.Configuration.create(
            business_profile={"headline": "PredictIQ Sports"},
            features={
                "invoice_history": {"enabled": True},
                "payment_method_update": {"enabled": True},
            },
        )
        return created.get("id")
    except Exception:
        return None

# ---------- endpoints ----------

@router.get("/diagnostics")
async def diagnostics():
    return {
        "has_secret": bool(settings.STRIPE_SECRET_KEY),
        "monthly_set": bool(settings.STRIPE_PRICE_MONTHLY),
        "quarterly_set": bool(settings.STRIPE_PRICE_QUARTERLY),
        "yearly_set": bool(settings.STRIPE_PRICE_YEARLY),
        "app_base_url": settings.APP_BASE_URL,
        "api_base_url": settings.API_BASE_URL,
        "portal_conf_set": bool(getattr(settings, "STRIPE_PORTAL_CONFIGURATION_ID", "")),
    }

@router.get("/portal-configs")
async def list_portal_configs():
    ensure_configured()
    try:
        res = stripe.billing_portal.Configuration.list(limit=10)
        data = [{"id": c.get("id"), "active": c.get("active"), "is_default": c.get("is_default")} for c in res.get("data", [])]
        acct = stripe.Account.retrieve()
        return {"account": acct.get("id"), "count": len(data), "configs": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Stripe error: {e}")

@router.get("/status")
async def status_endpoint(user=Depends(require_auth), db: AsyncSession = Depends(get_db)):
    rec = (await db.execute(select(Subscription).where(Subscription.user_id == user["user"].id))).scalar_one_or_none()
    if not rec:
        return {"active": False, "status": None, "plan": None, "current_period_end": None, "stripe_customer_id": None}
    return {
        "active": bool(rec.status == "active" and (rec.current_period_end is None or rec.current_period_end > datetime.now(tz=timezone.utc))),
        "status": rec.status,
        "plan": rec.plan,
        "current_period_end": rec.current_period_end.isoformat() if rec.current_period_end else None,
        "stripe_customer_id": rec.stripe_customer_id,
    }

@router.post("/checkout-session")
async def create_checkout_session(plan: str, user=Depends(require_auth), db: AsyncSession = Depends(get_db)):
    ensure_configured()
    price_id = get_price_id(plan)
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{settings.APP_BASE_URL}/account?status=success&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.APP_BASE_URL}/pricing?status=cancel",
        client_reference_id=str(user["user"].id),
    )
    return {"url": session.url}

@router.post("/sync-checkout-session")
async def sync_checkout_session(session_id: str, user=Depends(require_auth), db: AsyncSession = Depends(get_db)):
    ensure_configured()
    try:
        sess = stripe.checkout.Session.retrieve(session_id, expand=["subscription.items.data.price","subscription.items.data.plan"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Stripe retrieve error: {e}")
    owner = sess.get("client_reference_id")
    if owner and owner != str(user["user"].id):
        raise HTTPException(status_code=403, detail="Session does not belong to this user")
    sub_id = sess.get("subscription")
    cust = sess.get("customer")
    status_val = "active" if sess.get("payment_status") == "paid" else None
    cpe = None
    plan_interval = None
    plan_count = None
    try:
        if isinstance(sub_id, dict):
            sub = sub_id
        elif sub_id:
            sub = stripe.Subscription.retrieve(sub_id, expand=["items.data.price","items.data.plan"])  # type: ignore[arg-type]
        else:
            sub = None
        if sub:
            cpe = sub.get("current_period_end")
            plan_interval, plan_count = _extract_plan_from_subscription(sub)
            if not status_val:
                status_val = sub.get("status")
    except Exception:
        pass
    await _upsert_sub(db, str(user["user"].id), cust, sub.get("id") if isinstance(sub, dict) else sub_id, status_val, cpe, plan_interval, plan_count)
    return {"ok": True}

@router.post("/portal-session")
async def create_portal_session(user=Depends(require_auth), db: AsyncSession = Depends(get_db)):
    rec = (await db.execute(select(Subscription).where(Subscription.user_id == user["user"].id))).scalar_one_or_none()
    if not rec or not rec.stripe_customer_id:
        raise HTTPException(status_code=404, detail="No Stripe customer on record. Subscribe first.")
    ensure_configured()
    conf_id = _auto_get_or_create_portal_configuration()
    kwargs = {
        "customer": rec.stripe_customer_id,
        "return_url": f"{settings.APP_BASE_URL}/account",
    }
    if conf_id:
        kwargs["configuration"] = conf_id
    try:
        ps = stripe.billing_portal.Session.create(**kwargs)
        return {"url": ps.url}
    except stripe.error.InvalidRequestError as e:
        raise HTTPException(status_code=400, detail=f"Stripe portal error: {e.user_message or e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Stripe error: {e}")

# ----- Webhook handler -----
from fastapi import APIRouter as _APIRouter
webhooks = _APIRouter()

@webhooks.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if not settings.STRIPE_WEBHOOK_SECRET:
        return {"ok": True, "skipped": True}
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    etype = event["type"]
    data = event["data"]["object"]
    if etype == "checkout.session.completed":
        user_id = data.get("client_reference_id")
        customer = data.get("customer")
        subs = data.get("subscription")
        await _upsert_sub(db, user_id, customer, subs, "active", None, None, None)
    elif etype in ("customer.subscription.updated","customer.subscription.created","customer.subscription.deleted"):
        interval, interval_count = _extract_plan_from_subscription(data)
        user_id = (data.get("metadata") or {}).get("user_id")
        status_val = data.get("status")
        cpe = data.get("current_period_end")
        subs = data.get("id")
        customer = data.get("customer")
        if user_id:
            await _upsert_sub(db, user_id, customer, subs, status_val, cpe, interval, interval_count)
    return {"received": True}
