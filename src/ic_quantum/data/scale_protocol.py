"""Reproducible parameter protocol for the first scaled causal dataset."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Any


@dataclass(frozen=True, slots=True)
class ScaledDatasetConfig:
    dataset_id: str = "fase2_dataset_001"
    schema_version: str = "1.0"
    rate_values_rad_s: tuple[float, ...] = (0.5, 1.0, 2.0)
    time_min_s: float = 0.0
    time_max_s: float = 2.0 * math.pi
    time_points: int = 25
    probe_ids: tuple[str, ...] = ("0", "1", "+", "-", "+i", "-i")
    identifiability_atol: float = 1e-10

    def __post_init__(self) -> None:
        if self.time_points < 2:
            raise ValueError("time_points must be at least 2.")
        if self.time_min_s < 0 or self.time_max_s <= self.time_min_s:
            raise ValueError("Require 0 <= time_min_s < time_max_s.")
        if not self.rate_values_rad_s or any(rate <= 0 for rate in self.rate_values_rad_s):
            raise ValueError("All rate values must be positive.")
        if not self.probe_ids:
            raise ValueError("At least one probe state is required.")

    @property
    def time_values_s(self) -> tuple[float, ...]:
        step = (self.time_max_s - self.time_min_s) / (self.time_points - 1)
        return tuple(self.time_min_s + index * step for index in range(self.time_points))

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["time_values_s"] = list(self.time_values_s)
        payload["coverage_rationale"] = (
            "Normalized theoretical coverage: rates span a factor four around 1 rad/s; "
            "the time window [0,2*pi] s resolves identity, partial evolution, complete "
            "single-excitation exchange and recurrences through the dimensionless products "
            "delta_omega*t and g*t. These are controlled model units, not hardware calibration."
        )
        return payload

    def config_hash(self) -> str:
        encoded = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()
