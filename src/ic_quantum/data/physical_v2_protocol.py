"""Configuration for the physical-source causal-agent dataset v2.

The v1 dataset remains frozen. V2 uses source-specific time grids because a
magnetic-field pulse, a GHz acoustic mode, a quasiparticle burst and a slow
charge fluctuator do not share a physically meaningful common clock scale.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from ic_quantum.core.probes import FINAL_PROBE_IDS


def _linear(stop: float, count: int) -> tuple[float, ...]:
    return tuple(float(v) for v in np.linspace(0.0, stop, count))


def _zero_log(start: float, stop: float, count: int) -> tuple[float, ...]:
    if count < 2:
        raise ValueError("count must be >= 2.")
    return (
        0.0,
        *tuple(
            float(v)
            for v in np.logspace(np.log10(start), np.log10(stop), count - 1)
        ),
    )


@dataclass(frozen=True, slots=True)
class PhysicalV2Config:
    dataset_id: str = "ic_causal_agents_physical_v2"
    schema_version: str = "2.0"
    probe_ids: tuple[str, ...] = FINAL_PROBE_IDS
    identifiability_atol: float = 1e-10

    em_gyromagnetic_ratio: float = 1.76085962784e11
    em_field_amplitudes_t: tuple[float, ...] = (1e-8, 1e-7, 1e-6)
    em_drive_frequencies_hz: tuple[float, ...] = (0.0, 1e5, 1e6)
    em_orientations: tuple[str, ...] = ("x", "z")
    em_gaussian_sigma_b_t: tuple[float, ...] = (1e-8, 1e-7, 1e-6)
    em_time_max_s: float = 10e-6
    em_time_points: int = 41

    thermal_mode_counts: tuple[int, ...] = (4, 16)
    thermal_cutoffs_rad_s: tuple[float, ...] = (1.0, 2.0)
    thermal_temperature_ratios: tuple[float, ...] = (0.1, 1.0)
    thermal_time_max_s: float = 2.0 * np.pi
    thermal_time_points: int = 41

    photon_decay_rates_s: tuple[float, ...] = (1e4, 2e4, 1e5)
    photon_time_max_s: float = 200e-6
    photon_time_points: int = 41

    mechanical_frequencies_hz: tuple[float, ...] = (1e9, 3e9)
    mechanical_couplings_hz: tuple[float, ...] = (1e6, 5e6)
    mechanical_temperatures_k: tuple[float, ...] = (0.0, 0.05)
    mechanical_mode_dimension: int = 10
    mechanical_time_max_s: float = 1e-6
    mechanical_time_points: int = 41

    radiation_initial_xqp: tuple[float, ...] = (1e-6, 1e-5, 1e-4)
    radiation_trapping_rates_s: tuple[float, ...] = (1e3, 1e4)
    radiation_recombination_rate_s: float = 1.0 / 170e-9
    radiation_generation_rate_s: float = 0.0
    radiation_qubit_frequency_hz: float = 5e9
    radiation_background_relaxation_rate_s: float = 1e4
    radiation_time_min_positive_s: float = 1e-8
    radiation_time_max_s: float = 1e-2
    radiation_time_points: int = 41

    charge_couplings_hz: tuple[float, ...] = (1e3, 1e4, 1e5)
    charge_switching_rates_s: tuple[float, ...] = (1e3, 1e4, 1e5)
    charge_time_min_positive_s: float = 1e-7
    charge_time_max_s: float = 1e-2
    charge_time_points: int = 41

    @property
    def em_times_s(self) -> tuple[float, ...]:
        return _linear(self.em_time_max_s, self.em_time_points)

    @property
    def thermal_times_s(self) -> tuple[float, ...]:
        return _linear(self.thermal_time_max_s, self.thermal_time_points)

    @property
    def photon_times_s(self) -> tuple[float, ...]:
        return _linear(self.photon_time_max_s, self.photon_time_points)

    @property
    def mechanical_times_s(self) -> tuple[float, ...]:
        return _linear(self.mechanical_time_max_s, self.mechanical_time_points)

    @property
    def radiation_times_s(self) -> tuple[float, ...]:
        return _zero_log(
            self.radiation_time_min_positive_s,
            self.radiation_time_max_s,
            self.radiation_time_points,
        )

    @property
    def charge_times_s(self) -> tuple[float, ...]:
        return _zero_log(
            self.charge_time_min_positive_s,
            self.charge_time_max_s,
            self.charge_time_points,
        )

    @property
    def em_parameter_count(self) -> int:
        coherent = (
            len(self.em_field_amplitudes_t)
            * len(self.em_drive_frequencies_hz)
            * len(self.em_orientations)
        )
        return coherent + len(self.em_gaussian_sigma_b_t)

    @property
    def thermal_parameter_count(self) -> int:
        return (
            len(self.thermal_mode_counts)
            * len(self.thermal_cutoffs_rad_s)
            * len(self.thermal_temperature_ratios)
        )

    @property
    def mechanical_parameter_count(self) -> int:
        return (
            len(self.mechanical_frequencies_hz)
            * len(self.mechanical_couplings_hz)
            * len(self.mechanical_temperatures_k)
        )

    @property
    def radiation_parameter_count(self) -> int:
        return len(self.radiation_initial_xqp) * len(self.radiation_trapping_rates_s)

    @property
    def charge_parameter_count(self) -> int:
        return len(self.charge_couplings_hz) * len(self.charge_switching_rates_s)

    @property
    def expected_sample_count(self) -> int:
        probes = len(self.probe_ids)
        return probes * (
            self.em_parameter_count * self.em_time_points
            + self.thermal_parameter_count * self.thermal_time_points
            + len(self.photon_decay_rates_s) * self.photon_time_points
            + self.mechanical_parameter_count * self.mechanical_time_points
            + self.radiation_parameter_count * self.radiation_time_points
            + self.charge_parameter_count * self.charge_time_points
        )

    def __post_init__(self) -> None:
        if self.mechanical_mode_dimension < 2:
            raise ValueError("mechanical_mode_dimension must be >=2.")
        if self.identifiability_atol <= 0:
            raise ValueError("identifiability_atol must be positive.")
        if not self.probe_ids:
            raise ValueError("probe_ids cannot be empty.")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["expected_sample_count"] = self.expected_sample_count
        payload["time_grids_s"] = {
            "external_em": list(self.em_times_s),
            "thermal_bosonic": list(self.thermal_times_s),
            "photon_reservoir": list(self.photon_times_s),
            "mechanical": list(self.mechanical_times_s),
            "ionizing_radiation": list(self.radiation_times_s),
            "charge_rtn": list(self.charge_times_s),
        }
        payload["coverage_rationale"] = {
            "external_em": (
                "Semiclassical spin-field model; amplitudes and frequencies are a "
                "declared theoretical sensitivity grid, not hardware calibration."
            ),
            "thermal_bosonic": (
                "Existing exact finite-mode spin-boson model in natural units; "
                "temperature ratios and mode counts probe dephasing and revivals."
            ),
            "photon_reservoir": (
                "T1-like rates from 10 to 100 microseconds as a theoretical "
                "two-level-system relaxation grid."
            ),
            "mechanical": (
                "GHz acoustic modes and MHz qubit-phonon couplings are representative "
                "of circuit quantum acoustodynamics; 0 and 50 mK compare vacuum and thermal populations."
            ),
            "ionizing_radiation": (
                "Event-conditioned post-impact quasiparticle fractions and millisecond "
                "trapping; energy-deposition-to-x_qp conversion is not inferred."
            ),
            "charge_rtn": (
                "Log-spaced observation times cover slow/fast switching relative to "
                "kHz-100 kHz frequency-shift amplitudes; theoretical regime grid."
            ),
        }
        return payload

    def config_hash(self) -> str:
        raw = json.dumps(
            self.to_dict(), sort_keys=True, separators=(",", ":")
        ).encode()
        return hashlib.sha256(raw).hexdigest()


def load_physical_v2_config(path: str | Path) -> PhysicalV2Config:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    kwargs = dict(payload)
    for derived in ("expected_sample_count", "time_grids_s", "coverage_rationale"):
        kwargs.pop(derived, None)
    tuple_fields = {
        "probe_ids",
        "em_field_amplitudes_t",
        "em_drive_frequencies_hz",
        "em_orientations",
        "em_gaussian_sigma_b_t",
        "thermal_mode_counts",
        "thermal_cutoffs_rad_s",
        "thermal_temperature_ratios",
        "photon_decay_rates_s",
        "mechanical_frequencies_hz",
        "mechanical_couplings_hz",
        "mechanical_temperatures_k",
        "radiation_initial_xqp",
        "radiation_trapping_rates_s",
        "charge_couplings_hz",
        "charge_switching_rates_s",
    }
    for field in tuple_fields:
        if field in kwargs:
            kwargs[field] = tuple(kwargs[field])
    return PhysicalV2Config(**kwargs)
