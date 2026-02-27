from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    floors = Column(Integer, nullable=False)
    plot_id = Column(Integer, ForeignKey("plots.id"))