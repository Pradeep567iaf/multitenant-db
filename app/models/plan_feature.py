from sqlalchemy import Column, Integer, ForeignKey
from ..db.session import Base


class PlanFeature(Base):
    __tablename__ = "plan_features"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    feature_id = Column(Integer, ForeignKey("features.id"), nullable=False)
