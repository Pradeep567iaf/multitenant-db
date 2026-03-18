from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, Date, Numeric
from sqlalchemy.orm import relationship
from ..db.session import Base
from datetime import datetime


class Billing(Base):
    __tablename__ = "billings"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    feature_code = Column(String, nullable=True)  # Allow null for aggregated billing
    usage_count = Column(Integer, default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    total_cost = Column(Numeric(10, 2), nullable=True)  # For backward compatibility
    billing_period_start = Column(Date, nullable=False)
    billing_period_end = Column(Date, nullable=False)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    tenant = relationship("Tenant", back_populates="billings")
    feature_usages = relationship("FeatureUsage", back_populates="billing", cascade="all, delete-orphan")


class FeatureUsage(Base):
    __tablename__ = "feature_usages"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    feature_code = Column(String, nullable=False)
    usage_count = Column(Integer, default=1)
    total_cost = Column(Numeric(10, 2), nullable=False)
    billing_id = Column(Integer, ForeignKey("billings.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    tenant = relationship("Tenant", back_populates="feature_usages")
    billing = relationship("Billing", back_populates="feature_usages")
