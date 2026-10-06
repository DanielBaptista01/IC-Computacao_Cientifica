"""Agent-noise-entropy quantitative summaries for the final corpus."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ic_quantum.data.causal_agent_schema import CausalAgentSampleRecord


def analyze_agent_noise_entropy(
    samples: list[CausalAgentSampleRecord],
    *,
    atol: float = 1e-10,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for sample in samples:
        metrics = sample.signature.informational_metrics
        rows.append(
            {
                "agent_model_id": sample.agent_model_id,
                "probe_id": sample.initial_system_state,
                "parameter_point_id": sample.metadata["parameter_point_id"],
                "time_s": float(sample.time),
                "delta_entropy": float(metrics["delta_entropy"]),
                "delta_purity": float(metrics["delta_purity"]),
                "delta_coherence_l1": float(metrics["delta_coherence_l1"]),
                "fidelity_to_input": float(metrics["fidelity_to_input"]),
                "trace_distance_to_input": float(
                    metrics["trace_distance_to_input"]
                ),
                "entropy_after": float(metrics["entropy_after"]),
                "purity_after": float(metrics["purity_after"]),
                "coherence_l1_after": float(metrics["coherence_l1_after"]),
            }
        )
    frame = pd.DataFrame(rows)

    summary_rows = []
    for agent, group in frame.groupby("agent_model_id"):
        perturbed = group["trace_distance_to_input"] > atol
        entropy_unchanged = np.abs(group["delta_entropy"]) <= atol
        summary_rows.append(
            {
                "agent_model_id": agent,
                "samples": len(group),
                "max_trace_distance_to_input": float(
                    group["trace_distance_to_input"].max()
                ),
                "min_fidelity_to_input": float(group["fidelity_to_input"].min()),
                "max_abs_delta_entropy": float(
                    np.abs(group["delta_entropy"]).max()
                ),
                "max_abs_delta_purity": float(
                    np.abs(group["delta_purity"]).max()
                ),
                "max_abs_delta_coherence_l1": float(
                    np.abs(group["delta_coherence_l1"]).max()
                ),
                "perturbed_samples": int(perturbed.sum()),
                "perturbed_with_entropy_unchanged": int(
                    np.sum(perturbed & entropy_unchanged)
                ),
                "fraction_perturbed_with_entropy_unchanged": (
                    float(np.mean(entropy_unchanged[perturbed]))
                    if int(perturbed.sum()) > 0
                    else 0.0
                ),
            }
        )
    return frame, pd.DataFrame(summary_rows)


def representative_temporal_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """One fixed parameter point and |+> probe per agent for report figures."""
    selected = []
    for agent, group in frame.groupby("agent_model_id"):
        probe_group = group[group["probe_id"] == "+"]
        parameter_point = sorted(probe_group["parameter_point_id"].unique())[0]
        selected.append(
            probe_group[probe_group["parameter_point_id"] == parameter_point].copy()
        )
    return pd.concat(selected, ignore_index=True)
