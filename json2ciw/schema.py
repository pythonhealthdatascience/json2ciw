# schema.py
from typing import List, Literal, Dict
from pydantic import BaseModel, Field

class Distribution(BaseModel):
    name: Literal["exponential", "triangular", "uniform", "deterministic"]
    parameters: Dict[str, float]

class Resource(BaseModel):
    name: str
    count: int = Field(..., gt=0)

class Activity(BaseModel):
    name: str
    distribution: Distribution
    resource: Resource

class Transition(BaseModel):
    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    probability: float = Field(..., ge=0.0, le=1.0)

class ProcessModel(BaseModel):
    """The Full Queuing Network Description"""
    name: str
    inter_arrival_time: Distribution
    activities: List[Activity]
    transitions: List[Transition]
