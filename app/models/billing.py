from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from ..db.session import Base
from datetime import datetime


class Billing(Base):
    __tablename__ = "billings"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    feature_code = Column(String, nullable=False)
    usage_count = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    billing_period_start = Column(DateTime, default=datetime.utcnow)
    billing_period_end = Column(DateTime)
    is_sent = Column(Boolean, default=False)  # Email sent flag
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    tenant = relationship("Tenant", back_populates="billings")


class FeatureUsage(Base):
    __tablename__ = "feature_usages"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    feature_code = Column(String, nullable=False)
    used_at = Column(DateTime, default=datetime.utcnow)
    cost = Column(Float, nullable=False)

    # Relationship
    tenant = relationship("Tenant", back_populates="feature_usages")
