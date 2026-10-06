"""N-agent identifiability analysis for the final one-qubit causal corpus."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
import json
from typing import Any

import numpy as np
import pandas as pd

from ic_quantum.data.causal_agent_schema import CausalAgentSampleRecord


def _bloch(sample: CausalAgentSampleRecord) -> np.ndarray:
    obs = sample.signature.observables
    return np.asarray([obs["X"], obs["Y"], obs["Z"]], dtype=float)


def _qubit_trace_distance_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """For qubits, D(rho,sigma)=|r-s|_2/2 in Bloch representation."""
    return 0.5 * np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2)


def _group_samples(samples: list[CausalAgentSampleRecord]):
    groups: dict[tuple[str, str, float], list[CausalAgentSampleRecord]] = defaultdict(list)
    for sample in samples:
        groups[
            (sample.agent_model_id, sample.initial_system_state, float(sample.time))
        ].append(sample)
    return groups


def analyze_pairwise_identifiability(
    samples: list[CausalAgentSampleRecord],
    *,
    atol: float,
) -> dict[str, pd.DataFrame]:
    agents = sorted({sample.agent_model_id for sample in samples})
    probes = sorted({sample.initial_system_state for sample in samples})
    times = sorted({float(sample.time) for sample in samples})
    groups = _group_samples(samples)

    condition_rows: list[dict[str, Any]] = []
    collision_rows: list[dict[str, Any]] = []

    for agent_a, agent_b in combinations(agents, 2):
        for probe in probes:
            for time in times:
                a_samples = groups[(agent_a, probe, time)]
                b_samples = groups[(agent_b, probe, time)]
                a_bloch = np.vstack([_bloch(sample) for sample in a_samples])
                b_bloch = np.vstack([_bloch(sample) for sample in b_samples])
                distances = _qubit_trace_distance_matrix(a_bloch, b_bloch)
                min_flat = int(np.argmin(distances))
                i_min, j_min = np.unravel_index(min_flat, distances.shape)
                minimum = float(distances[i_min, j_min])
                collisions = int(np.sum(distances <= atol))
                row = {
                    "agent_a": agent_a,
                    "agent_b": agent_b,
                    "probe_id": probe,
                    "time_s": time,
                    "parameter_pair_comparisons": int(distances.size),
                    "collision_pair_count": collisions,
                    "collision_pair_fraction": collisions / float(distances.size),
                    "min_trace_distance": minimum,
                    "mean_trace_distance": float(np.mean(distances)),
                    "median_trace_distance": float(np.median(distances)),
                    "max_trace_distance": float(np.max(distances)),
                    "closest_parameter_point_a": a_samples[i_min].metadata[
                        "parameter_point_id"
                    ],
                    "closest_parameter_point_b": b_samples[j_min].metadata[
                        "parameter_point_id"
                    ],
                }
                condition_rows.append(row)
                if minimum <= atol:
                    collision_rows.append(
                        {
                            **row,
                            "parameter_values_a_json": json.dumps(
                                a_samples[i_min].parameter_values, sort_keys=True
                            ),
                            "parameter_values_b_json": json.dumps(
                                b_samples[j_min].parameter_values, sort_keys=True
                            ),
                        }
                    )

    conditions = pd.DataFrame(condition_rows)
    collisions = pd.DataFrame(collision_rows)

    pair_rows = []
    for (agent_a, agent_b), frame in conditions.groupby(["agent_a", "agent_b"]):
        pair_rows.append(
            {
                "agent_a": agent_a,
                "agent_b": agent_b,
                "probe_time_conditions": len(frame),
                "conditions_with_collision": int(
                    np.sum(frame["min_trace_distance"] <= atol)
                ),
                "condition_collision_fraction": float(
                    np.mean(frame["min_trace_distance"] <= atol)
                ),
                "parameter_pair_comparisons": int(
                    frame["parameter_pair_comparisons"].sum()
                ),
                "collision_pair_count": int(frame["collision_pair_count"].sum()),
                "collision_pair_fraction": float(
                    frame["collision_pair_count"].sum()
                    / frame["parameter_pair_comparisons"].sum()
                ),
                "mean_condition_min_trace_distance": float(
                    frame["min_trace_distance"].mean()
                ),
                "median_condition_min_trace_distance": float(
                    frame["min_trace_distance"].median()
                ),
                "global_mean_trace_distance": float(
                    np.average(
                        frame["mean_trace_distance"],
                        weights=frame["parameter_pair_comparisons"],
                    )
                ),
                "max_trace_distance": float(frame["max_trace_distance"].max()),
            }
        )
    pair_summary = pd.DataFrame(pair_rows)

    probe_rows = []
    for (agent_a, agent_b, probe), frame in conditions.groupby(
        ["agent_a", "agent_b", "probe_id"]
    ):
        probe_rows.append(
            {
                "agent_a": agent_a,
                "agent_b": agent_b,
                "probe_id": probe,
                "conditions": len(frame),
                "collision_condition_fraction": float(
                    np.mean(frame["min_trace_distance"] <= atol)
                ),
                "mean_min_trace_distance": float(frame["min_trace_distance"].mean()),
                "max_trace_distance": float(frame["max_trace_distance"].max()),
            }
        )
    probe_summary = pd.DataFrame(probe_rows)

    temporal_rows = []
    for (agent_a, agent_b, time), frame in conditions.groupby(
        ["agent_a", "agent_b", "time_s"]
    ):
        temporal_rows.append(
            {
                "agent_a": agent_a,
                "agent_b": agent_b,
                "time_s": time,
                "collision_condition_fraction": float(
                    np.mean(frame["min_trace_distance"] <= atol)
                ),
                "mean_min_trace_distance": float(frame["min_trace_distance"].mean()),
            }
        )
    temporal_summary = pd.DataFrame(temporal_rows)

    mean_matrix = pd.DataFrame(0.0, index=agents, columns=agents)
    collision_matrix = pd.DataFrame(0.0, index=agents, columns=agents)
    for row in pair_rows:
        a, b = row["agent_a"], row["agent_b"]
        mean_matrix.loc[a, b] = mean_matrix.loc[b, a] = row[
            "mean_condition_min_trace_distance"
        ]
        collision_matrix.loc[a, b] = collision_matrix.loc[b, a] = row[
            "condition_collision_fraction"
        ]

    return {
        "condition_pairwise": conditions,
        "collision_regions": collisions,
        "pair_summary": pair_summary,
        "probe_summary": probe_summary,
        "temporal_summary": temporal_summary,
        "mean_min_distance_matrix": mean_matrix,
        "collision_fraction_matrix": collision_matrix,
    }


def analyze_intra_agent_variation(
    samples: list[CausalAgentSampleRecord],
    *,
    atol: float,
) -> dict[str, pd.DataFrame]:
    groups = _group_samples(samples)
    condition_rows: list[dict[str, Any]] = []

    for (agent, probe, time), group in groups.items():
        if len(group) < 2:
            continue
        bloch = np.vstack([_bloch(sample) for sample in group])
        distances = _qubit_trace_distance_matrix(bloch, bloch)
        tri = distances[np.triu_indices(len(group), k=1)]
        condition_rows.append(
            {
                "agent_model_id": agent,
                "probe_id": probe,
                "time_s": time,
                "parameter_pair_comparisons": len(tri),
                "collision_pair_count": int(np.sum(tri <= atol)),
                "collision_pair_fraction": float(np.mean(tri <= atol)),
                "mean_trace_distance": float(np.mean(tri)),
                "min_trace_distance": float(np.min(tri)),
                "max_trace_distance": float(np.max(tri)),
            }
        )

    condition_columns = [
        "agent_model_id",
        "probe_id",
        "time_s",
        "parameter_pair_comparisons",
        "collision_pair_count",
        "collision_pair_fraction",
        "mean_trace_distance",
        "min_trace_distance",
        "max_trace_distance",
    ]
    conditions = pd.DataFrame(condition_rows, columns=condition_columns)
    summary_rows = []
    for agent, frame in conditions.groupby("agent_model_id"):
        summary_rows.append(
            {
                "agent_model_id": agent,
                "probe_time_conditions": len(frame),
                "parameter_pair_comparisons": int(
                    frame["parameter_pair_comparisons"].sum()
                ),
                "collision_pair_fraction": float(
                    frame["collision_pair_count"].sum()
                    / frame["parameter_pair_comparisons"].sum()
                ),
                "mean_trace_distance": float(
                    np.average(
                        frame["mean_trace_distance"],
                        weights=frame["parameter_pair_comparisons"],
                    )
                ),
                "mean_condition_min_trace_distance": float(
                    frame["min_trace_distance"].mean()
                ),
            }
        )
    summary = pd.DataFrame(
        summary_rows,
        columns=[
            "agent_model_id",
            "probe_time_conditions",
            "parameter_pair_comparisons",
            "collision_pair_fraction",
            "mean_trace_distance",
            "mean_condition_min_trace_distance",
        ],
    )

    temporal_groups: dict[
        tuple[str, str, str], list[CausalAgentSampleRecord]
    ] = defaultdict(list)
    for sample in samples:
        temporal_groups[
            (
                sample.agent_model_id,
                sample.initial_system_state,
                sample.metadata["parameter_point_id"],
            )
        ].append(sample)

    adjacent_rows = []
    for (agent, probe, parameter_point), group in temporal_groups.items():
        ordered = sorted(group, key=lambda sample: float(sample.time))
        distances = [
            0.5 * float(np.linalg.norm(_bloch(right) - _bloch(left)))
            for left, right in zip(ordered, ordered[1:])
        ]
        if distances:
            adjacent_rows.append(
                {
                    "agent_model_id": agent,
                    "probe_id": probe,
                    "parameter_point_id": parameter_point,
                    "adjacent_time_comparisons": len(distances),
                    "mean_adjacent_trace_distance": float(np.mean(distances)),
                    "max_adjacent_trace_distance": float(np.max(distances)),
                }
            )
    adjacent = pd.DataFrame(
        adjacent_rows,
        columns=[
            "agent_model_id",
            "probe_id",
            "parameter_point_id",
            "adjacent_time_comparisons",
            "mean_adjacent_trace_distance",
            "max_adjacent_trace_distance",
        ],
    )
    if adjacent.empty:
        adjacent_summary = pd.DataFrame(
            columns=[
                "agent_model_id",
                "mean_adjacent_trace_distance",
                "max_adjacent_trace_distance",
            ]
        )
    else:
        adjacent_summary = (
            adjacent.groupby("agent_model_id", as_index=False)
            .agg(
                mean_adjacent_trace_distance=("mean_adjacent_trace_distance", "mean"),
                max_adjacent_trace_distance=("max_adjacent_trace_distance", "max"),
            )
        )

    return {
        "intra_condition": conditions,
        "intra_summary": summary,
        "adjacent_temporal": adjacent,
        "adjacent_temporal_summary": adjacent_summary,
    }
