from pydantic import BaseModel, Field

class Plot(BaseModel):
    length: float = Field(gt=0)
    width: float = Field(gt=0)
    road_width: float = Field(gt=0)

class Building(BaseModel):
    floors: int = Field(gt=0)

class GenerateRequest(BaseModel):
    plot: Plot
    building: Building