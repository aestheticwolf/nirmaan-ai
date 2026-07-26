from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Authority(Base):
    __tablename__ = "authorities"

    id = Column(BigInteger, primary_key=True, index=True)
    state_id = Column(BigInteger, ForeignKey("states.id"))
    district_id = Column(BigInteger)
    name = Column(String)
    authority_type = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())