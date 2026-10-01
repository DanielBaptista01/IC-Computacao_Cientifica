"""Controlled identifiability analysis for matched causal-agent samples."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

import numpy as np

from ic_quantum.data.causal_agent_schema import CausalAgentSampleRecord
from ic_quantum.data.state_encoding import decode_complex_matrix
from ic_quantum.metrics.distance import trace_distance


@dataclass(frozen=True, slots=True)
class IdentifiabilityPair:
    probe_id: str
    rate_value_rad_s: float
    time_s: float
    trace_distance: float
    distinguishable: bool


def sample_density_matrix(sample: CausalAgentSampleRecord) -> np.ndarray:
    payload = sample.signature.extra["simulated_density_matrix"]
    return decode_complex_matrix(payload)


def _key(sample: CausalAgentSampleRecord) -> tuple[str, float, float]:
    return (
        sample.initial_system_state,
        float(sample.metadata["rate_value_rad_s"]),
        float(sample.time),
    )


def matched_inter_agent_trace_distances(
    samples: list[CausalAgentSampleRecord],
    agent_a: str,
    agent_b: str,
    *,
    atol: float = 1e-10,
) -> list[IdentifiabilityPair]:
    index_a = {_key(s): s for s in samples if s.agent_model_id == agent_a}
    index_b = {_key(s): s for s in samples if s.agent_model_id == agent_b}
    common = sorted(set(index_a).intersection(index_b))
    pairs: list[IdentifiabilityPair] = []
    for probe_id, rate, time in common:
        distance = trace_distance(
            sample_density_matrix(index_a[(probe_id, rate, time)]),
            sample_density_matrix(index_b[(probe_id, rate, time)]),
        )
        pairs.append(
            IdentifiabilityPair(
                probe_id=probe_id,
                rate_value_rad_s=rate,
                time_s=time,
                trace_distance=distance,
                distinguishable=bool(distance > atol),
            )
        )
    return pairs


def adjacent_intra_agent_trace_distances(
    samples: list[CausalAgentSampleRecord],
    agent_id: str,
) -> list[float]:
    groups: dict[tuple[str, float], list[CausalAgentSampleRecord]] = defaultdict(list)
    for sample in samples:
        if sample.agent_model_id == agent_id:
            groups[
                (
                    sample.initial_system_state,
                    float(sample.metadata["rate_value_rad_s"]),
                )
            ].append(sample)

    distances: list[float] = []
    for group in groups.values():
        ordered = sorted(group, key=lambda sample: float(sample.time))
        for left, right in zip(ordered, ordered[1:]):
            distances.append(
                trace_distance(
                    sample_density_matrix(left),
                    sample_density_matrix(right),
                )
            )
    return distances


def summarize_identifiability(
    samples: list[CausalAgentSampleRecord],
    agent_a: str,
    agent_b: str,
    *,
    atol: float = 1e-10,
) -> dict[str, Any]:
    pairs = matched_inter_agent_trace_distances(
        samples, agent_a, agent_b, atol=atol
    )
    per_probe: dict[str, dict[str, Any]] = {}
    for probe in sorted({pair.probe_id for pair in pairs}):
        values = [pair.trace_distance for pair in pairs if pair.probe_id == probe]
        nonidentifiable = sum(value <= atol for value in values)
        per_probe[probe] = {
            "comparisons": len(values),
            "nonidentifiable_count": nonidentifiable,
            "nonidentifiable_fraction": nonidentifiable / len(values),
            "mean_trace_distance": float(np.mean(values)),
            "min_trace_distance": float(np.min(values)),
            "max_trace_distance": float(np.max(values)),
        }

    inter = np.asarray([pair.trace_distance for pair in pairs], dtype=float)
    intra_a = np.asarray(
        adjacent_intra_agent_trace_distances(samples, agent_a), dtype=float
    )
    intra_b = np.asarray(
        adjacent_intra_agent_trace_distances(samples, agent_b), dtype=float
    )

    return {
        "agent_a": agent_a,
        "agent_b": agent_b,
        "matched_comparisons": len(pairs),
        "nonidentifiable_count": int(np.sum(inter <= atol)),
        "nonidentifiable_fraction": float(np.mean(inter <= atol)),
        "inter_trace_distance_mean": float(np.mean(inter)),
        "inter_trace_distance_median": float(np.median(inter)),
        "inter_trace_distance_min": float(np.min(inter)),
        "inter_trace_distance_max": float(np.max(inter)),
        "adjacent_intra_trace_distance_mean": {
            agent_a: float(np.mean(intra_a)),
            agent_b: float(np.mean(intra_b)),
        },
        "per_probe": per_probe,
        "interpretation_guard": (
            "The adjacent-intra versus matched-inter comparison is grid-dependent and "
            "is reported descriptively; it is not a proof of globally unique causal identity."
        ),
    }
