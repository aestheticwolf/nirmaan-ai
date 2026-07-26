from sqlalchemy import Column, BigInteger, Numeric, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class ComplianceResult(Base):
    __tablename__ = "compliance_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    design_id = Column(UUID(as_uuid=True), ForeignKey("designs.id"), nullable=True)
    rule_id = Column(BigInteger, ForeignKey("rules.id"))
    status = Column(Text)
    actual_value = Column(Numeric)
    expected_value = Column(Numeric)
    remarks = Column(Text)
    evaluated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())