from sqlalchemy import Column, Integer, String, Text, DateTime, func
from .database import Base

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    signature_html = Column(Text, nullable=True)
    archetype = Column(String(100), nullable=True, default="custom")
    stripe_session_id = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending")
    amount = Column(Integer, nullable=False, default=199)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
