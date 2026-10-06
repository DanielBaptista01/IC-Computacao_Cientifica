"""Frozen configuration schema for the IC 2026 final causal-agent dataset."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from ic_quantum.core.probes import FINAL_PROBE_IDS


@dataclass(frozen=True, slots=True)
class FinalDatasetConfig:
    dataset_id: str = "ic_causal_agents_final_v1"
    schema_version: str = "1.0"
    time_min_s: float = 0.0
    time_max_s: float = 4.0 * math.pi
    time_points: int = 81
    probe_ids: tuple[str, ...] = FINAL_PROBE_IDS
    coherent_detuning_rates: tuple[float, ...] = (0.25, 0.5, 0.75, 1.0, 1.5)
    finite_exchange_couplings: tuple[float, ...] = (0.25, 0.5, 0.75, 1.0, 1.5)
    photon_decay_rates: tuple[float, ...] = (0.05, 0.1, 0.25, 0.5, 1.0)
    spin_boson_mode_counts: tuple[int, ...] = (2, 4, 16, 64)
    spin_boson_cutoffs: tuple[float, ...] = (1.0, 2.0)
    spin_boson_temperature_ratios: tuple[float, ...] = (0.5, 1.0)
    identifiability_atol: float = 1e-10

    def __post_init__(self) -> None:
        if self.time_points < 2:
            raise ValueError("time_points must be >=2.")
        if self.time_min_s < 0 or self.time_max_s <= self.time_min_s:
            raise ValueError("Require 0 <= time_min_s < time_max_s.")
        if any(v <= 0 for v in self.coherent_detuning_rates):
            raise ValueError("coherent_detuning_rates must be positive.")
        if any(v <= 0 for v in self.finite_exchange_couplings):
            raise ValueError("finite_exchange_couplings must be positive.")
        if any(v <= 0 for v in self.photon_decay_rates):
            raise ValueError("photon_decay_rates must be positive.")
        if any(v <= 0 for v in self.spin_boson_mode_counts):
            raise ValueError("spin_boson_mode_counts must be positive.")
        if any(v <= 0 for v in self.spin_boson_cutoffs):
            raise ValueError("spin_boson_cutoffs must be positive.")
        if any(v < 0 for v in self.spin_boson_temperature_ratios):
            raise ValueError("spin_boson_temperature_ratios must be non-negative.")

    @property
    def time_values_s(self) -> tuple[float, ...]:
        return tuple(
            float(v)
            for v in np_linspace(self.time_min_s, self.time_max_s, self.time_points)
        )

    @property
    def spin_boson_parameter_count(self) -> int:
        return (
            len(self.spin_boson_mode_counts)
            * len(self.spin_boson_cutoffs)
            * len(self.spin_boson_temperature_ratios)
        )

    @property
    def expected_sample_count(self) -> int:
        probe_time = len(self.probe_ids) * self.time_points
        return probe_time * (
            len(self.coherent_detuning_rates)
            + len(self.finite_exchange_couplings)
            + len(self.photon_decay_rates)
            + self.spin_boson_parameter_count
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["time_values_s"] = list(self.time_values_s)
        payload["expected_sample_count"] = self.expected_sample_count
        payload["coverage_rationale"] = {
            "states": (
                "Six Pauli-axis eigenstates plus eight symmetric cube-vertex pure "
                "states increase Bloch-sphere coverage without random sampling."
            ),
            "time": (
                "The [0,4*pi] normalized theoretical window resolves zero-time limits, "
                "coherent cycles, finite-exchange recurrences and finite-mode bath revivals."
            ),
            "rates": (
                "Coherent/exchange/Markovian rates span weak-to-strong normalized regimes; "
                "they are theoretical coverage values, not hardware calibrations."
            ),
            "spin_boson": (
                "Mode count 2..64 probes the finite-bath crossover; two cutoffs and two "
                "temperature ratios vary memory and dephasing time scales."
            ),
        }
        return payload

    def config_hash(self) -> str:
        raw = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()


def np_linspace(start: float, stop: float, count: int) -> list[float]:
    # Kept explicit to avoid coupling the configuration schema to NumPy serialization.
    step = (stop - start) / (count - 1)
    return [start + index * step for index in range(count)]


def load_final_dataset_config(path: str | Path) -> FinalDatasetConfig:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return FinalDatasetConfig(
        dataset_id=payload["dataset_id"],
        schema_version=payload.get("schema_version", "1.0"),
        time_min_s=float(payload["time_min_s"]),
        time_max_s=float(payload["time_max_s"]),
        time_points=int(payload["time_points"]),
        probe_ids=tuple(payload["probe_ids"]),
        coherent_detuning_rates=tuple(float(v) for v in payload["coherent_detuning_rates"]),
        finite_exchange_couplings=tuple(float(v) for v in payload["finite_exchange_couplings"]),
        photon_decay_rates=tuple(float(v) for v in payload["photon_decay_rates"]),
        spin_boson_mode_counts=tuple(int(v) for v in payload["spin_boson_mode_counts"]),
        spin_boson_cutoffs=tuple(float(v) for v in payload["spin_boson_cutoffs"]),
        spin_boson_temperature_ratios=tuple(
            float(v) for v in payload["spin_boson_temperature_ratios"]
        ),
        identifiability_atol=float(payload.get("identifiability_atol", 1e-10)),
    )
