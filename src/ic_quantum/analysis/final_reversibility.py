"""Per-condition reversibility analysis for the final causal corpus."""

from __future__ import annotations

import pandas as pd

from ic_quantum.data.causal_agent_schema import CausalAgentSampleRecord


def analyze_reversibility(
    samples: list[CausalAgentSampleRecord],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    unique: dict[tuple[str, str, float], dict] = {}
    for sample in samples:
        key = (
            sample.agent_model_id,
            sample.metadata["parameter_point_id"],
            float(sample.time),
        )
        if key not in unique:
            channel = sample.signature.channel_descriptors
            unique[key] = {
                "agent_model_id": sample.agent_model_id,
                "parameter_point_id": sample.metadata["parameter_point_id"],
                "time_s": float(sample.time),
                "reversibility_class": channel["reversibility_class"],
                "linear_invertible": channel["linear_invertible"],
                "analytical_linear_invertible": channel.get(
                    "analytical_linear_invertible", channel["linear_invertible"]
                ),
                "numerical_linear_invertible_at_tolerance": channel.get(
                    "numerical_linear_invertible_at_tolerance",
                    channel["linear_invertible"],
                ),
                "inverse_cptp": channel["inverse_cptp"],
                "direct_unitary_inverse": channel["direct_unitary_inverse"],
                "choi_rank": channel["choi_rank"],
                "condition_number": channel["condition_number"],
            }
    conditions = pd.DataFrame(unique.values())
    summary = (
        conditions.groupby(["agent_model_id", "reversibility_class"], as_index=False)
        .size()
        .rename(columns={"size": "condition_count"})
    )
    totals = conditions.groupby("agent_model_id").size().to_dict()
    summary["fraction_within_agent"] = summary.apply(
        lambda row: row["condition_count"] / totals[row["agent_model_id"]],
        axis=1,
    )
    return conditions, summary
