import uuid
import stripe
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..models import Purchase

router = APIRouter(prefix="/api", tags=["checkout"])

class CreateCheckoutRequest(BaseModel):
    email: EmailStr
    signatureHtml: str
    archetype: str = "custom"

@router.post("/create-checkout-session")
def create_checkout_session(req: CreateCheckoutRequest, db: Session = Depends(get_db)):
    secret_key = settings.STRIPE_SECRET_KEY
    is_mock = not secret_key or "Mock" in secret_key

    if not is_mock:
        stripe.api_key = secret_key
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "SigHub Master Email Signature",
                            "description": "Full portable HTML signature export & delivery",
                        },
                        "unit_amount": 199,
                    },
                    "quantity": 1,
                }],
                mode="payment",
                customer_email=req.email,
                success_url=f"{settings.BASE_URL}/builder.html?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.BASE_URL}/builder.html?canceled=true",
            )
            session_id = session.id
            session_url = session.url
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Stripe session creation failed: {str(e)}")
    else:
        mock_id = f"cs_test_{uuid.uuid4().hex[:12]}"
        session_id = mock_id
        session_url = f"{settings.BASE_URL}/builder.html?session_id={mock_id}&mock_checkout=true"

    purchase = Purchase(
        email=req.email,
        signature_html=req.signatureHtml,
        archetype=req.archetype,
        stripe_session_id=session_id,
        status="pending",
        amount=199
    )
    db.add(purchase)
    db.commit()

    return {"url": session_url, "sessionId": session_id}

@router.get("/purchase-status/{session_id}")
def get_purchase_status(session_id: str, db: Session = Depends(get_db)):
    purchase = db.query(Purchase).filter(Purchase.stripe_session_id == session_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase session not found")

    return {
        "status": purchase.status,
        "email": purchase.email,
        "signatureHtml": purchase.signature_html,
        "createdAt": purchase.created_at.isoformat() if purchase.created_at else None
    }
