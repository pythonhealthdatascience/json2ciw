from typing import List, Literal, Dict, Optional, Set
from pydantic import BaseModel, Field, model_validator
from collections import defaultdict

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

    @model_validator(mode="after")
    def validate_transition_rows(self) -> "ProcessModel":
        activity_names: Set[str] = {a.name for a in self.activities}
        allowed_targets = activity_names | {"Exit"}

        # 1) Validate references + accumulate outgoing probs per source
        probs_by_source = defaultdict(float)

        for t in self.transitions:
            if t.source not in activity_names:
                raise ValueError(f"Transition 'from' unknown activity: {t.source}")
            if t.target not in allowed_targets:
                raise ValueError(f"Transition 'to' unknown target: {t.target}")
            probs_by_source[t.source] += t.probability

        # 2) Require every activity to have an outgoing total of exactly 1.0
        tol = 1e-9
        missing_sources = []
        bad_sums = []

        for a in self.activities:
            total = probs_by_source.get(a.name, 0.0)
            if total == 0.0:
                missing_sources.append(a.name)
            elif abs(total - 1.0) > tol:
                bad_sums.append((a.name, total))

        if missing_sources:
            raise ValueError(
                "Missing outgoing transitions for activities (sum=0.0): "
                + ", ".join(missing_sources)
            )

        if bad_sums:
            details = ", ".join([f"{name} (sum={total})" for name, total in bad_sums])
            raise ValueError(
                "Outgoing transition probabilities must sum to 1.0 for each activity; "
                f"problems: {details}"
            )

        print("Transitions sum to 1.0 for all activities.")

        return self



