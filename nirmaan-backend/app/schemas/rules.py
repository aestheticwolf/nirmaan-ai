from pydantic import BaseModel

class PlotSchema(BaseModel):
    length: float
    width: float
    roadWidth: float

class BuildingSchema(BaseModel):
    floors: int
    far: float
    coverage: float

class RuleRequest(BaseModel):
    plot: PlotSchema
    building: BuildingSchema
    state: str