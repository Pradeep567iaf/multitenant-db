from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base


class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)  # "F1", "F2", "F3", "F4"
    name = Column(String, nullable=False)
    cost = Column(Float, nullable=False)  # Cost per use in dollars

    # Relationships
    plans = relationship("Plan", secondary="plan_features", back_populates="features")
