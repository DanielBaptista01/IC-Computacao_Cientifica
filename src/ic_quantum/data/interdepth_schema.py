"""Schema for the minimal inter-depth latent-causal experiment."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class InterdepthExperimentRecord:
    experiment_id: str
    case_id: str
    transform_id: str
    agent_id: str | None
    agent_parameters: dict[str, Any]
    initial_state: str
    programmed_gate_1: str
    programmed_gate_2: str
    interval_start_depth: int
    interval_end_depth: int
    transform_kind: str

    entropy_after_latent: float
    purity_after_latent: float
    coherence_after_latent: float
    fidelity_to_interval_target: float

    direct_unitary_inverse_available: bool
    direct_recovery_applied: bool
    recovery_fidelity_at_interval: float | None
    max_unitary_recovery_fidelity_bound: float

    final_fidelity_uncorrected: float
    final_fidelity_after_direct_recovery: float | None

    reversibility_class: str
    linear_invertible: bool | None
    inverse_cptp: bool | None
    direct_unitary_inverse: bool | None
    random_seed: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
