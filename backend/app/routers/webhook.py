import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..models import Purchase
from ..email import send_receipt_and_signature

router = APIRouter(prefix="/api", tags=["webhook"])

@router.post("/stripe-webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if not stripe_signature or not webhook_secret:
        raise HTTPException(
            status_code=400,
            detail="Missing stripe-signature header or STRIPE_WEBHOOK_SECRET configuration"
        )

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=webhook_secret
        )
    except Exception as e:
        print(f"[WEBHOOK SIGNATURE ERROR] Verification failed: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Webhook Signature Verification Error: {str(e)}"
        )

    print(f"[WEBHOOK RECEIVED] Event: {event['type']} [{event['id']}]")

    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]
        session_id = getattr(session_obj, "id", None) or (session_obj.to_dict().get("id") if hasattr(session_obj, "to_dict") else None)

        purchase = db.query(Purchase).filter(Purchase.stripe_session_id == session_id).first()
        if purchase:
            purchase.status = "paid"
            db.commit()
            print(f"[WEBHOOK SUCCESS] Marked session {session_id} as paid in Postgres")
            send_receipt_and_signature(purchase.email, purchase.signature_html, session_id)
        else:
            print(f"[WEBHOOK WARN] Session ID {session_id} not found in database")

    return {"received": True}
