from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..models import Purchase

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/stats")
def get_admin_stats(
    x_admin_secret: str = Header(None, alias="x-admin-secret"),
    admin_secret: str = Query(None),
    db: Session = Depends(get_db)
):
    provided_secret = x_admin_secret or admin_secret
    if not provided_secret or provided_secret != settings.ADMIN_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing admin secret."
        )

    total_purchases = db.query(func.count(Purchase.id)).scalar() or 0
    paid_purchases = db.query(func.count(Purchase.id)).filter(Purchase.status == "paid").scalar() or 0
    revenue_cents = db.query(func.sum(Purchase.amount)).filter(Purchase.status == "paid").scalar() or 0
    revenue_usd = f"{(revenue_cents / 100):.2f}"

    archetype_rows = db.query(
        Purchase.archetype, func.count(Purchase.id)
    ).group_by(Purchase.archetype).all()

    archetypes_map = {row[0] or "custom": row[1] for row in archetype_rows}

    recent_purchases = db.query(Purchase).order_by(Purchase.created_at.desc()).limit(50).all()

    purchases_list = [
        {
            "id": p.id,
            "email": p.email,
            "archetype": p.archetype,
            "stripe_session_id": p.stripe_session_id,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in recent_purchases
    ]

    return {
        "totalPurchases": total_purchases,
        "paidPurchases": paid_purchases,
        "revenueUSD": revenue_usd,
        "archetypes": archetypes_map,
        "recentPurchases": purchases_list
    }
