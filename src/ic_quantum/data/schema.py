"""Schema for one reproducible experimental observation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class ExperimentRecord:
    experiment_id: str
    agent_id: str
    initial_state: str
    agent_parameters: dict[str, Any]
    channel_type: str
    time: float | None
    entropy_before: float
    entropy_after: float
    purity_before: float
    purity_after: float
    coherence_before: float
    coherence_after: float
    fidelity_to_ideal: float
    recovery_fidelity: float | None
    reversibility_class: str
    random_seed: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
