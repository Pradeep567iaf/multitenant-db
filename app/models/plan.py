from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from ..db.session import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # "Basic" or "Advanced"
    description = Column(Text)
    created_at = Column(String)

    # Relationships
    features = relationship("Feature", secondary="plan_features", back_populates="plans")
    tenants = relationship("Tenant", back_populates="plan")
