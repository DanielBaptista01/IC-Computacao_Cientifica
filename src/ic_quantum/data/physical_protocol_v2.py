"""Configuration for the physically expanded causal-agent dataset v2."""

from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json, math
from pathlib import Path
from typing import Any
from ic_quantum.core.probes import FINAL_PROBE_IDS
from ic_quantum.data.final_protocol import FinalDatasetConfig, np_linspace


@dataclass(frozen=True, slots=True)
class PhysicalV2Config:
    dataset_id: str = "ic_causal_agents_physical_v2"
    schema_version: str = "2.0"
    time_min_s: float = 0.0
    time_max_s: float = 2.0e-6
    time_points: int = 41
    probe_ids: tuple[str, ...] = FINAL_PROBE_IDS

    coherent_detuning_rates: tuple[float, ...] = (1.5707963268e6, 3.1415926536e6, 6.2831853072e6)
    finite_exchange_couplings: tuple[float, ...] = (1.5707963268e6, 3.1415926536e6, 6.2831853072e6)
    photon_decay_rates: tuple[float, ...] = (2.5e5, 5.0e5, 1.0e6)
    spin_boson_mode_counts: tuple[int, ...] = (4, 8)
    spin_boson_cutoffs: tuple[float, ...] = (3.1415926536e6, 6.2831853072e6)
    spin_boson_temperature_ratios: tuple[float, ...] = (0.5, 1.0)

    em_rabi_rates: tuple[float, ...] = (1.5707963268e6, 6.2831853072e6)
    em_detunings: tuple[float, ...] = (0.0, 3.1415926536e6)
    em_phases: tuple[float, ...] = (0.0, math.pi/2)

    magnetic_field_amplitudes_t: tuple[float, ...] = (1.0e-6, 5.0e-6, 1.0e-5)
    magnetic_orientations: tuple[str, ...] = ("x","z","xz")
    gyromagnetic_ratio_rad_s_t: float = 2.0 * math.pi * 28.0e9

    thermal_decay_rates: tuple[float, ...] = (2.5e5, 1.0e6)
    thermal_temperatures_k: tuple[float, ...] = (0.02, 0.10, 0.50)
    thermal_transition_angular_frequency: float = 2.0 * math.pi * 5.0e9

    mechanical_mode_frequencies: tuple[float, ...] = (2.0*math.pi*0.5e6, 2.0*math.pi*1.0e6)
    mechanical_couplings: tuple[float, ...] = (2.0*math.pi*0.05e6, 2.0*math.pi*0.10e6)
    mechanical_occupations: tuple[float, ...] = (0.0, 1.0, 5.0)

    identifiability_atol: float = 1e-10

    @property
    def time_values_s(self) -> tuple[float, ...]:
        return tuple(np_linspace(self.time_min_s,self.time_max_s,self.time_points))

    @property
    def base_config(self) -> FinalDatasetConfig:
        return FinalDatasetConfig(
            dataset_id=self.dataset_id+"__baseline_component",
            schema_version=self.schema_version,
            time_min_s=self.time_min_s,
            time_max_s=self.time_max_s,
            time_points=self.time_points,
            probe_ids=self.probe_ids,
            coherent_detuning_rates=self.coherent_detuning_rates,
            finite_exchange_couplings=self.finite_exchange_couplings,
            photon_decay_rates=self.photon_decay_rates,
            spin_boson_mode_counts=self.spin_boson_mode_counts,
            spin_boson_cutoffs=self.spin_boson_cutoffs,
            spin_boson_temperature_ratios=self.spin_boson_temperature_ratios,
            identifiability_atol=self.identifiability_atol,
        )

    @property
    def new_physical_parameter_count(self) -> int:
        return (
            len(self.em_rabi_rates)*len(self.em_detunings)*len(self.em_phases)
            + len(self.magnetic_field_amplitudes_t)*len(self.magnetic_orientations)
            + len(self.thermal_decay_rates)*len(self.thermal_temperatures_k)
            + len(self.mechanical_mode_frequencies)*len(self.mechanical_couplings)*len(self.mechanical_occupations)
        )

    @property
    def expected_sample_count(self) -> int:
        return self.base_config.expected_sample_count + len(self.probe_ids)*self.time_points*self.new_physical_parameter_count

    def to_dict(self) -> dict[str,Any]:
        payload=asdict(self)
        payload["time_values_s"]=list(self.time_values_s)
        payload["expected_sample_count"]=self.expected_sample_count
        payload["coverage_rationale"]={
            "time":"0..2 microseconds: theoretical common observation window for MHz-scale effective couplings; not hardware calibration.",
            "em":"Rabi rate/detuning/phase vary coherent EM response; raw E0 is not inferred without a platform dipole matrix element.",
            "magnetic":"B amplitudes 1..10 microtesla with an explicitly marked electron-spin-like gamma reference; not device calibration.",
            "thermal":"5 GHz transition with 20 mK, 100 mK and 500 mK probes low-to-thermally-populated photon regimes.",
            "mechanical":"0.5/1 MHz modes, two coupling ratios and three occupations test frequency, coupling and thermal population.",
        }
        return payload

    def config_hash(self) -> str:
        return hashlib.sha256(json.dumps(self.to_dict(),sort_keys=True,separators=(",",":")).encode()).hexdigest()


def load_physical_v2_config(path: str|Path) -> PhysicalV2Config:
    p=json.loads(Path(path).read_text(encoding="utf-8"))
    fields={k:v for k,v in p.items() if k not in {"time_values_s","expected_sample_count","coverage_rationale"}}
    tuple_fields=[
        "probe_ids","coherent_detuning_rates","finite_exchange_couplings","photon_decay_rates",
        "spin_boson_mode_counts","spin_boson_cutoffs","spin_boson_temperature_ratios",
        "em_rabi_rates","em_detunings","em_phases","magnetic_field_amplitudes_t",
        "magnetic_orientations","thermal_decay_rates","thermal_temperatures_k",
        "mechanical_mode_frequencies","mechanical_couplings","mechanical_occupations",
    ]
    for key in tuple_fields:
        if key in fields:
            fields[key]=tuple(fields[key])
    return PhysicalV2Config(**fields)
