from sqlalchemy import Column, Integer, Float
from app.database import Base

class Plot(Base):
    __tablename__ = "plots"

    id = Column(Integer, primary_key=True, index=True)
    length = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    road_width = Column(Float, nullable=False)