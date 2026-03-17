from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..db.session import Base


class SuperAdmin(Base):
    __tablename__ = "super_admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(String)

    # Relationship to tenants created by this superadmin
    tenants_created = relationship("Tenant", back_populates="created_by_superadmin")
