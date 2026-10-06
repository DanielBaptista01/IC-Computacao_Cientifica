"""Generate, validate and analyze the first scaled scientific causal dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from ic_quantum.analysis.identifiability import (
    matched_inter_agent_trace_distances,
    summarize_identifiability,
)
from ic_quantum.data.export import export_scientific_dataset
from ic_quantum.data.generator import generate_scaled_first_lot_samples
from ic_quantum.data.scale_protocol import (
    ScaledDatasetConfig,
    load_scaled_dataset_config,
)


AGENT_A = "coherent-longitudinal-detuning"
AGENT_B = "finite-two-level-exchange-relaxation"


def run_scaled_dataset_experiment(
    output_dir: Path,
    config: ScaledDatasetConfig,
) -> dict:
    samples = generate_scaled_first_lot_samples(config)
    exported = export_scientific_dataset(samples, config, output_dir)

    pairs = matched_inter_agent_trace_distances(
        samples,
        AGENT_A,
        AGENT_B,
        atol=config.identifiability_atol,
    )
    pair_frame = pd.DataFrame(
        [
            {
                "probe_id": pair.probe_id,
                "rate_value_rad_s": pair.rate_value_rad_s,
                "time_s": pair.time_s,
                "trace_distance": pair.trace_distance,
                "distinguishable": pair.distinguishable,
            }
            for pair in pairs
        ]
    )
    pair_path = output_dir / "matched_identifiability_pairs.csv"
    pair_frame.to_csv(pair_path, index=False)

    identifiability = summarize_identifiability(
        samples,
        AGENT_A,
        AGENT_B,
        atol=config.identifiability_atol,
    )
    reversibility_counts: dict[str, int] = {}
    for sample in samples:
        classification = str(
            sample.signature.channel_descriptors["reversibility_class"]
        )
        reversibility_counts[classification] = (
            reversibility_counts.get(classification, 0) + 1
        )

    summary = {
        "dataset_id": config.dataset_id,
        "N_A": len({sample.agent_model_id for sample in samples}),
        "N_S": len(samples),
        "C_theta": {
            "rate_values_rad_s": list(config.rate_values_rad_s),
            "rate_count": len(config.rate_values_rad_s),
            "time_min_s": config.time_min_s,
            "time_max_s": config.time_max_s,
            "time_points": config.time_points,
            "probe_states": list(config.probe_ids),
            "probe_count": len(config.probe_ids),
            "cartesian_samples_per_agent": (
                len(config.rate_values_rad_s)
                * config.time_points
                * len(config.probe_ids)
            ),
        },
        "reversibility_class_counts": reversibility_counts,
        "identifiability": identifiability,
        "scientific_scope": {
            "machine_learning_trained": False,
            "claim_of_unique_agent_signature": False,
            "parameter_range_type": "normalized_theoretical_validation_range",
            "interpretation": (
                "This dataset is the first scaled controlled corpus for the two "
                "individually validated LEVEL_3 causal models; it is not the final IC corpus."
            ),
        },
        "files": {name: str(path.name) for name, path in exported.items()},
        "identifiability_pairs_file": pair_path.name,
    }

    summary_path = output_dir / "dataset_analysis_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/generated/validated/fase2_dataset_001"),
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Optional JSON configuration. Defaults to the controlled protocol.",
    )
    args = parser.parse_args()

    config = (
        load_scaled_dataset_config(args.config)
        if args.config
        else ScaledDatasetConfig()
    )
    run_scaled_dataset_experiment(args.output_dir, config)


if __name__ == "__main__":
    main()
