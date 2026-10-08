"""Controlled non-identifiability experiment for two physical dephasing sources.

A thermal finite-mode spin-boson source and a quasistatic Gaussian magnetic-field
source are parameterized to produce the same reduced dephasing map at one snapshot.
Their normalized trajectories are then compared away from that matched endpoint.

This demonstrates:
    identical reduced map at one observation time != identical physical cause.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ic_quantum.core.probes import standard_probe_densities
from ic_quantum.dynamics.external_field import (
    gaussian_quasistatic_field_coherence_factor,
    gaussian_quasistatic_field_kraus,
)
from ic_quantum.dynamics.open_system import apply_kraus
from ic_quantum.dynamics.spin_boson import (
    finite_mode_coherence_factor,
    spin_boson_dephasing_kraus,
)


def _trace_distance(rho: np.ndarray, sigma: np.ndarray) -> float:
    delta = np.asarray(rho - sigma, dtype=complex)
    eigvals = np.linalg.eigvalsh(0.5 * (delta + delta.conjugate().T))
    return float(0.5 * np.sum(np.abs(eigvals)))


def matched_em_thermal_dephasing_experiment(
    config,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return summary and normalized trajectory for a matched dephasing snapshot."""
    mode_count = int(config.thermal_mode_counts[0])
    cutoff = float(config.thermal_cutoffs_rad_s[0])
    temperature_ratio = float(config.thermal_temperature_ratios[-1])
    temperature = temperature_ratio * cutoff

    # Use a dense deterministic search rather than the dataset storage grid.
    # The experiment asks whether two continuous physical models can coincide at
    # a snapshot; it should not depend on whether the stored dataset sampled that
    # exact time.
    search_times = np.linspace(
        0.0, float(config.thermal_time_max_s), 2001
    )
    search_q = np.asarray(
        [
            finite_mode_coherence_factor(
                time=float(t),
                mode_count=mode_count,
                cutoff_angular_frequency=cutoff,
                temperature_angular_frequency=temperature,
            )
            for t in search_times
        ],
        dtype=float,
    )
    nontrivial = np.where(
        (search_times > 0.0) & (search_q < 1.0 - 1e-10) & (search_q > 1e-12)
    )[0]
    if len(nontrivial) == 0:
        raise RuntimeError(
            "Could not select a nontrivial thermal dephasing snapshot."
        )
    index = int(
        nontrivial[
            np.argmin(np.abs(search_q[nontrivial] - 0.70))
        ]
    )
    thermal_time = float(search_times[index])
    q_target = float(search_q[index])

    em_time = 0.8 * float(config.em_time_max_s)
    gamma = float(config.em_gyromagnetic_ratio)
    sigma_b = float(
        np.sqrt(-2.0 * np.log(q_target)) / (gamma * em_time)
    )
    q_em = gaussian_quasistatic_field_coherence_factor(
        gyromagnetic_ratio=gamma,
        field_standard_deviation=sigma_b,
        time=em_time,
    )

    thermal_kraus = spin_boson_dephasing_kraus(q_target)
    em_kraus = gaussian_quasistatic_field_kraus(
        gyromagnetic_ratio=gamma,
        field_standard_deviation=sigma_b,
        time=em_time,
    )
    distances = []
    for rho in standard_probe_densities().values():
        thermal_out = apply_kraus(rho, thermal_kraus)
        em_out = apply_kraus(rho, em_kraus)
        distances.append(_trace_distance(thermal_out, em_out))

    normalized = np.linspace(0.0, 1.0, 101)
    trajectory_rows = []
    shape_differences = []
    for u in normalized:
        thermal_q = finite_mode_coherence_factor(
            time=float(u * thermal_time),
            mode_count=mode_count,
            cutoff_angular_frequency=cutoff,
            temperature_angular_frequency=temperature,
        )
        em_q = gaussian_quasistatic_field_coherence_factor(
            gyromagnetic_ratio=gamma,
            field_standard_deviation=sigma_b,
            time=float(u * em_time),
        )
        difference = abs(float(thermal_q) - float(em_q))
        shape_differences.append(difference)
        trajectory_rows.append(
            {
                "normalized_time": float(u),
                "thermal_spin_boson_coherence": float(thermal_q),
                "em_gaussian_coherence": float(em_q),
                "absolute_coherence_difference": float(difference),
            }
        )

    summary = pd.DataFrame(
        [
            {
                "source_a": "external-magnetic-field-wave",
                "source_b": "finite-mode-spin-boson-dephasing",
                "matched_reduced_channel": "pure_dephasing",
                "target_coherence_factor": q_target,
                "em_coherence_factor_at_match": float(q_em),
                "thermal_snapshot_time_natural_units": thermal_time,
                "em_snapshot_time_s": em_time,
                "derived_em_sigma_b_t": sigma_b,
                "thermal_mode_count": mode_count,
                "thermal_cutoff_rad_s": cutoff,
                "thermal_temperature_ratio": temperature_ratio,
                "max_probe_trace_distance_at_matched_snapshot": float(
                    max(distances)
                ),
                "max_normalized_trajectory_coherence_difference": float(
                    max(shape_differences)
                ),
                "endpoint_coherence_difference": float(
                    shape_differences[-1]
                ),
                "interpretation": (
                    "The two physical causes are operationally non-identifiable "
                    "from this matched reduced-channel snapshot alone; normalized "
                    "temporal response supplies additional distinguishing information."
                ),
            }
        ]
    )
    return summary, pd.DataFrame(trajectory_rows)
