from sqlalchemy import Column, BigInteger, String, Boolean, Date, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Regulation(Base):
    __tablename__ = "regulations"

    id = Column(BigInteger, primary_key=True, index=True)
    authority_id = Column(BigInteger, ForeignKey("authorities.id"))
    name = Column(String)
    version_number = Column(String)
    effective_from = Column(Date)
    effective_to = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())