from typing import List, Literal, Dict, Optional
from pydantic import BaseModel, Field

class Distribution(BaseModel):
    type: Literal["exponential", "triangular", "uniform", "deterministic"]
    parameters: Dict[str, float]

class Resource(BaseModel):
    name: str
    capacity: int = Field(..., gt=0)

class Activity(BaseModel):
    name: str
    type: str
    resource: Resource
    service_distribution: Distribution
    # Optional because not all nodes have arrivals
    arrival_distribution: Optional[Distribution] = None

class Transition(BaseModel):
    source: str = Field(..., alias="from")
    target: str = Field(..., alias="to")
    probability: float = Field(..., ge=0.0, le=1.0)

class ProcessModel(BaseModel):
    name: str
    description: Optional[str] = None
    activities: List[Activity]
    transitions: List[Transition]
