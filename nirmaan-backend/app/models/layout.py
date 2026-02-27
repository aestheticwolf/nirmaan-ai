from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Layout(Base):
    __tablename__ = "layouts"

    id = Column(Integer, primary_key=True, index=True)
    plot_length = Column(Float)
    plot_width = Column(Float)
    floors = Column(Integer)
    far = Column(Float)
    coverage = Column(Float)
    file_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())