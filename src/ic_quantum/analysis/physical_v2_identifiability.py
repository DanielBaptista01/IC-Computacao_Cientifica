"""Identifiability analysis across physical-source families with different time scales."""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from ic_quantum.data.causal_agent_schema import CausalAgentSampleRecord


def _bloch(sample: CausalAgentSampleRecord) -> np.ndarray:
    obs = sample.signature.observables
    return np.asarray([obs["X"], obs["Y"], obs["Z"]], dtype=float)


def _group(samples):
    result = {}
    for sample in samples:
        result.setdefault(
            (sample.agent_model_id, sample.initial_system_state), []
        ).append(sample)
    return result


def _symmetric_nearest(
    a: np.ndarray, b: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    d_ab, _ = cKDTree(b).query(a, k=1)
    d_ba, _ = cKDTree(a).query(b, k=1)
    return 0.5 * np.asarray(d_ab), 0.5 * np.asarray(d_ba)


def analyze_physical_signature_overlap(
    samples,
    *,
    atol: float,
) -> dict[str, pd.DataFrame]:
    agents = sorted({sample.agent_model_id for sample in samples})
    probes = sorted({sample.initial_system_state for sample in samples})
    groups = _group(samples)
    probe_rows = []

    for agent_a, agent_b in combinations(agents, 2):
        for probe in probes:
            a_samples = groups[(agent_a, probe)]
            b_samples = groups[(agent_b, probe)]
            a = np.vstack([_bloch(sample) for sample in a_samples])
            b = np.vstack([_bloch(sample) for sample in b_samples])
            d_ab, d_ba = _symmetric_nearest(a, b)
            nearest = np.concatenate([d_ab, d_ba])

            a_nonzero = [s for s in a_samples if float(s.time) > 0.0]
            b_nonzero = [s for s in b_samples if float(s.time) > 0.0]
            if a_nonzero and b_nonzero:
                nz_a = np.vstack([_bloch(s) for s in a_nonzero])
                nz_b = np.vstack([_bloch(s) for s in b_nonzero])
                nz_ab, nz_ba = _symmetric_nearest(nz_a, nz_b)
                nonzero_min = float(
                    min(np.min(nz_ab), np.min(nz_ba))
                )
            else:
                nonzero_min = float("nan")

            probe_rows.append(
                {
                    "agent_a": agent_a,
                    "agent_b": agent_b,
                    "probe_id": probe,
                    "samples_a": len(a_samples),
                    "samples_b": len(b_samples),
                    "minimum_trace_distance": float(np.min(nearest)),
                    "minimum_nonzero_time_trace_distance": nonzero_min,
                    "mean_symmetric_nearest_trace_distance": float(
                        np.mean(nearest)
                    ),
                    "median_symmetric_nearest_trace_distance": float(
                        np.median(nearest)
                    ),
                    "fraction_nearest_collision": float(
                        np.mean(nearest <= atol)
                    ),
                }
            )

    probe_summary = pd.DataFrame(probe_rows)
    pair_rows = []
    for (agent_a, agent_b), frame in probe_summary.groupby(
        ["agent_a", "agent_b"]
    ):
        pair_rows.append(
            {
                "agent_a": agent_a,
                "agent_b": agent_b,
                "probe_count": len(frame),
                "minimum_trace_distance": float(
                    frame["minimum_trace_distance"].min()
                ),
                "minimum_nonzero_time_trace_distance": float(
                    frame["minimum_nonzero_time_trace_distance"].min()
                ),
                "mean_nearest_trace_distance_across_probes": float(
                    frame["mean_symmetric_nearest_trace_distance"].mean()
                ),
                "mean_collision_fraction_across_probes": float(
                    frame["fraction_nearest_collision"].mean()
                ),
                "probes_with_any_exact_collision": int(
                    np.sum(frame["minimum_trace_distance"] <= atol)
                ),
            }
        )
    pair_summary = pd.DataFrame(pair_rows)

    overlap_matrix = pd.DataFrame(
        0.0, index=agents, columns=agents
    )
    for row in pair_rows:
        a, b = row["agent_a"], row["agent_b"]
        value = row["mean_nearest_trace_distance_across_probes"]
        overlap_matrix.loc[a, b] = overlap_matrix.loc[b, a] = value

    return {
        "physical_pair_summary": pair_summary,
        "physical_probe_overlap": probe_summary,
        "physical_mean_nearest_distance_matrix": overlap_matrix,
    }


def dephasing_source_trajectory_comparison(samples) -> pd.DataFrame:
    """Compare representative dephasing trajectory shapes on normalized clocks."""
    chosen = {
        "external-magnetic-field-wave": "stochastic_longitudinal_field",
        "finite-mode-spin-boson-dephasing": "thermal_bosonic_dephasing",
        "bistable-charge-fluctuator-rtn": "bistable_charge_fluctuation",
    }
    rows = []
    for agent, regime in chosen.items():
        group = [
            sample
            for sample in samples
            if sample.agent_model_id == agent
            and sample.initial_system_state == "+"
            and sample.metadata["physical_regime"] == regime
        ]
        parameter_point = sorted(
            {s.metadata["parameter_point_id"] for s in group}
        )[-1]
        trajectory = sorted(
            [
                s
                for s in group
                if s.metadata["parameter_point_id"] == parameter_point
            ],
            key=lambda s: float(s.time),
        )
        max_time = max(float(s.time) for s in trajectory)
        for sample in trajectory:
            rows.append(
                {
                    "agent_model_id": agent,
                    "parameter_point_id": parameter_point,
                    "time_s": float(sample.time),
                    "normalized_time": (
                        float(sample.time) / max_time
                        if max_time > 0
                        else 0.0
                    ),
                    "x_coherence_response": float(
                        sample.signature.observables["X"]
                    ),
                    "transverse_bloch_magnitude": float(
                        np.hypot(
                            sample.signature.observables["X"],
                            sample.signature.observables["Y"],
                        )
                    ),
                }
            )
    return pd.DataFrame(rows)
