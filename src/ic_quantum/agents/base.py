"""Data model for a causal agent without assuming a universal dynamics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(slots=True)
class CausalAgent:
    """Mathematical metadata associated with a hypothesized causal agent.

    The agent identity is deliberately separated from the effective channel: distinct
    physical causes may generate indistinguishable reduced dynamics.
    """

    agent_id: str
    name: str
    physical_model: str
    dynamic_regime: str
    parameters: dict[str, Any] = field(default_factory=dict)
    temporal_parameters: dict[str, Any] = field(default_factory=dict)
    interaction_hamiltonian: np.ndarray | None = None
    kraus_operators: list[np.ndarray] | None = None
    effective_channel: str | None = None
    reversibility_class: str | None = None
