# api/app/routers_billing.py
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone
import stripe
import uuid

from .auth import get_db, require_auth
from .config import settings
from .models import Subscription

# Ensure Stripe API key is set (defensive, in case main didn't set it yet)
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/v1/billing", tags=["billing"])

@router.get("/status")
async def billing_status(user=Depends(require_auth), db: AsyncSession = Depends(get_db)):
    u = user["user"]
    sub = (await db.execute(select(Subscription).where(Subscription.user_id == u.id))).scalar_one_or_none()
    if not sub:
        return {"status": "none", "plan": None, "current_period_end": None, "stripe_customer_id": None}
    return {
        "status": sub.status,
        "plan": sub.plan,
        "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
        "stripe_customer_id": sub.stripe_customer_id,
    }

@router.post("/checkout-session")
async def create_checkout_session(plan: str, user=Depends(require_auth), db: AsyncSession = Depends(get_db)):
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    price_map = {
        "monthly": settings.STRIPE_PRICE_MONTHLY,
        "quarterly": settings.STRIPE_PRICE_QUARTERLY,
        "yearly": settings.STRIPE_PRICE_YEARLY,
    }
    price_id = price_map.get(plan)
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid plan")
    u = user["user"]
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{settings.APP_BASE_URL}/account?status=success&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.APP_BASE_URL}/pricing?status=cancel",
        client_reference_id=u.id,
        customer_creation="always",
    )
    return {"url": session.url}

@router.post("/portal-session")
async def portal_session(user=Depends(require_auth), db: AsyncSession = Depends(get_db)):
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    u = user["user"]
    sub = (await db.execute(select(Subscription).where(Subscription.user_id == u.id))).scalar_one_or_none()
    if not sub or not sub.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer on file. Complete checkout first.")
    session = stripe.billing_portal.Session.create(
        customer=sub.stripe_customer_id,
        return_url=f"{settings.APP_BASE_URL}/account",
    )
    return {"url": session.url}

@router.post("/sync-checkout")
async def sync_checkout(session_id: str = Query(...), user=Depends(require_auth), db: AsyncSession = Depends(get_db)):
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    try:
        session = stripe.checkout.Session.retrieve(session_id, expand=["subscription", "customer"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve session: {e}")
    u = user["user"]
    customer_id = session.get("customer")
    sub_obj = session.get("subscription")
    subs_id = sub_obj.get("id") if isinstance(sub_obj, dict) else (sub_obj or None)
    status_val = sub_obj.get("status") if isinstance(sub_obj, dict) else None
    cpe = sub_obj.get("current_period_end") if isinstance(sub_obj, dict) else None
    plan_interval = None
    if isinstance(sub_obj, dict):
        items = sub_obj.get("items", {}).get("data", [])
        if items:
            plan_interval = items[0].get("plan", {}).get("interval")

    existing = (await db.execute(select(Subscription).where(Subscription.user_id == u.id))).scalar_one_or_none()
    now = datetime.now(tz=timezone.utc)
    cpe_dt = datetime.fromtimestamp(cpe, tz=timezone.utc) if cpe else None
    if existing:
        await db.execute(
            update(Subscription).where(Subscription.user_id == u.id).values(
                stripe_customer_id=customer_id,
                stripe_sub_id=subs_id,
                status=status_val or "active",
                current_period_end=cpe_dt,
                plan=plan_interval,
                updated_at=now,
            )
        )
    else:
        db.add(Subscription(
            id=str(uuid.uuid4()),
            user_id=u.id,
            stripe_customer_id=customer_id,
            stripe_sub_id=subs_id,
            status=status_val or "active",
            current_period_end=cpe_dt,
            plan=plan_interval,
            updated_at=now,
        ))
    await db.commit()
    return {"ok": True, "status": status_val or "active", "plan": plan_interval}

# ---- Webhooks router (REQUIRED by app.main import) ----
webhooks = APIRouter()

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

    async def upsert_sub(user_id: str, stripe_cust: str | None, stripe_sub: str | None, status_val: str | None, current_period_end: int | None, plan: str | None):
        cpe_dt = datetime.fromtimestamp(current_period_end, tz=timezone.utc) if current_period_end else None
        existing = (await db.execute(select(Subscription).where(Subscription.user_id == user_id))).scalar_one_or_none()
        now = datetime.now(tz=timezone.utc)
        if existing:
            await db.execute(
                update(Subscription).where(Subscription.user_id == user_id).values(
                    stripe_customer_id=stripe_cust,
                    stripe_sub_id=stripe_sub,
                    status=status_val,
                    current_period_end=cpe_dt,
                    plan=plan,
                    updated_at=now
                )
            )
        else:
            sub = Subscription(
                id=str(uuid.uuid4()),
                user_id=user_id,
                stripe_customer_id=stripe_cust,
                stripe_sub_id=stripe_sub,
                status=status_val,
                current_period_end=cpe_dt,
                plan=plan,
                updated_at=now
            )
            db.add(sub)
        await db.commit()

    # Minimal event mapping
    if etype == "checkout.session.completed":
        user_id = data.get("client_reference_id")
        customer = data.get("customer")
        subs = data.get("subscription")
        if user_id:
            await upsert_sub(user_id, customer, subs, "active", None, None)
    elif etype in ("customer.subscription.updated", "customer.subscription.created", "customer.subscription.deleted"):
        user_id = data.get("metadata", {}).get("user_id")
        status_val = data.get("status")
        current_period_end = data.get("current_period_end")
        subs = data.get("id")
        customer = data.get("customer")
        plan = (data.get("items", {}).get("data", [{}])[0].get("plan", {}).get("interval") if data.get("items") else None)
        if user_id:
            await upsert_sub(user_id, customer, subs, status_val, current_period_end, plan)

    return {"received": True}
