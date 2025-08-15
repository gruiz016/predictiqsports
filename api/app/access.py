# api/app/access.py
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .auth import require_auth, get_db
from .models import Subscription

async def require_active_subscription(user=Depends(require_auth), db: AsyncSession = Depends(get_db)):
    """Allow request to proceed only if the user has an active subscription.
    Active = status == 'active' AND (current_period_end is NULL OR current_period_end > now)
    Returns the same 'user' dict for downstream handlers.
    """
    rec = (await db.execute(select(Subscription).where(Subscription.user_id == user["user"].id))).scalar_one_or_none()
    now = datetime.now(tz=timezone.utc)
    active = bool(rec and rec.status == "active" and (rec.current_period_end is None or rec.current_period_end > now))
    if not active:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "subscription_required",
                "message": "An active subscription is required to access this feature.",
            },
        )
    return user
