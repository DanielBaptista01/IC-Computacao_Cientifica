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



PROCESS_PROBES: tuple[str, ...] = ("0", "1", "+", "+i")


def _process_condition_vectors(
    samples,
    required_probes: tuple[str, ...] = PROCESS_PROBES,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Build tomographically informative output vectors per dynamic condition.

    For each (agent, parameter point, time), concatenate the output Bloch vectors
    for four linearly independent qubit probes.  This is an operational process
    signature, not a diamond-norm channel representation.
    """
    grouped: dict[tuple[str, str, float], dict[str, CausalAgentSampleRecord]] = {}
    for sample in samples:
        key = (
            sample.agent_model_id,
            sample.metadata["parameter_point_id"],
            float(sample.time),
        )
        grouped.setdefault(key, {})[sample.initial_system_state] = sample

    per_agent: dict[str, list[tuple[float, np.ndarray]]] = {}
    for (agent, _point, time), by_probe in grouped.items():
        if not all(probe in by_probe for probe in required_probes):
            continue
        vector = np.concatenate(
            [_bloch(by_probe[probe]) for probe in required_probes]
        )
        per_agent.setdefault(agent, []).append((time, vector))

    result: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for agent, rows in per_agent.items():
        times = np.asarray([row[0] for row in rows], dtype=float)
        vectors = np.vstack([row[1] for row in rows])
        result[agent] = (times, vectors)
    return result


def analyze_process_signature_overlap(
    samples,
    *,
    atol: float,
    required_probes: tuple[str, ...] = PROCESS_PROBES,
) -> dict[str, pd.DataFrame]:
    """Compare physical sources using a multi-probe process-response embedding.

    Distance is the RMS one-qubit trace distance across the required probes:
        d = sqrt(mean_i D(rho_i^A, rho_i^B)^2).
    It is an operational protocol metric, not the diamond distance.
    """
    conditions = _process_condition_vectors(samples, required_probes)
    agents = sorted(conditions)
    scale = 0.5 / np.sqrt(float(len(required_probes)))
    rows = []

    for agent_a, agent_b in combinations(agents, 2):
        times_a, vectors_a = conditions[agent_a]
        times_b, vectors_b = conditions[agent_b]

        raw_ab, _ = cKDTree(vectors_b).query(vectors_a, k=1)
        raw_ba, _ = cKDTree(vectors_a).query(vectors_b, k=1)
        nearest = scale * np.concatenate([raw_ab, raw_ba])

        nz_a = vectors_a[times_a > 0.0]
        nz_b = vectors_b[times_b > 0.0]
        if len(nz_a) and len(nz_b):
            nz_ab, _ = cKDTree(nz_b).query(nz_a, k=1)
            nz_ba, _ = cKDTree(nz_a).query(nz_b, k=1)
            nonzero_min = float(
                scale * min(float(np.min(nz_ab)), float(np.min(nz_ba)))
            )
        else:
            nonzero_min = float("nan")

        rows.append(
            {
                "agent_a": agent_a,
                "agent_b": agent_b,
                "process_probe_count": len(required_probes),
                "conditions_a": len(vectors_a),
                "conditions_b": len(vectors_b),
                "minimum_process_signature_distance": float(np.min(nearest)),
                "minimum_nonzero_time_process_distance": nonzero_min,
                "mean_symmetric_nearest_process_distance": float(
                    np.mean(nearest)
                ),
                "median_symmetric_nearest_process_distance": float(
                    np.median(nearest)
                ),
                "fraction_nearest_process_collision": float(
                    np.mean(nearest <= atol)
                ),
            }
        )

    summary = pd.DataFrame(rows)
    matrix = pd.DataFrame(0.0, index=agents, columns=agents)
    for row in rows:
        a = row["agent_a"]
        b = row["agent_b"]
        value = row["mean_symmetric_nearest_process_distance"]
        matrix.loc[a, b] = matrix.loc[b, a] = value

    return {
        "process_pair_summary": summary,
        "process_mean_nearest_distance_matrix": matrix,
    }
