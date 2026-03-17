from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..db.session import Base
from datetime import datetime


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subdomain = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True)  # Null until first login
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_superadmin_id = Column(Integer, ForeignKey("super_admins.id"))

    # Relationships
    created_by_superadmin = relationship("SuperAdmin", back_populates="tenants_created")
    plan = relationship("Plan", back_populates="tenants")
    users = relationship("TenantUser", back_populates="tenant", cascade="all, delete-orphan")
    billings = relationship("Billing", back_populates="tenant", cascade="all, delete-orphan")
    feature_usages = relationship("FeatureUsage", back_populates="tenant", cascade="all, delete-orphan")
