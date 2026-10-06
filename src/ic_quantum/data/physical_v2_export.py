"""CSV/Parquet export for the physical-source v2 dataset."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import platform
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import scipy

from ic_quantum.data.final_export import (
    _feature_row,
    _scientific_row,
    _strict_json,
    current_git_sha,
)
from ic_quantum.data.physical_catalog import build_physical_source_registry
from ic_quantum.data.physical_v2_protocol import PhysicalV2Config


def export_physical_v2_dataset(
    samples,
    config: PhysicalV2Config,
    output_dir: Path,
):
    dataset_dir = output_dir / "dataset"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    registry = build_physical_source_registry()

    scientific_rows = []
    feature_rows = []
    label_rows = []
    for row_id, sample in enumerate(samples):
        model = registry.get(sample.agent_model_id)
        scientific = _scientific_row(row_id, sample, model)
        scientific.update(
            {
                "physical_source": model.physical_source,
                "causal_mechanism": model.causal_mechanism,
                "physical_parameters_json": _strict_json(
                    sample.signature.physical_parameters
                ),
                "physical_regime": sample.metadata["physical_regime"],
                "signature_extra_json": _strict_json(sample.signature.extra),
            }
        )
        scientific_rows.append(scientific)
        feature_rows.append(_feature_row(row_id, sample))
        label_rows.append(
            {
                "row_id": row_id,
                "sample_id": sample.sample_id,
                "agent_model_id": sample.agent_model_id,
                "physical_source": model.physical_source,
                "causal_mechanism": model.causal_mechanism,
            }
        )

    scientific = pd.DataFrame(scientific_rows)
    features = pd.DataFrame(feature_rows)
    labels = pd.DataFrame(label_rows)

    forbidden = {
        "agent_model_id",
        "agent_name",
        "physical_source",
        "causal_mechanism",
        "physical_category",
        "sample_id",
        "parameter_values_json",
        "physical_parameters_json",
        "physical_regime",
    }
    leaked = forbidden.intersection(features.columns)
    if leaked:
        raise RuntimeError(
            f"Causal-label leakage into observable features: {sorted(leaked)}"
        )

    paths = {
        "scientific_records_csv": dataset_dir / "scientific_records.csv",
        "scientific_records_parquet": dataset_dir / "scientific_records.parquet",
        "observable_features_csv": dataset_dir / "observable_features.csv",
        "observable_features_parquet": dataset_dir / "observable_features.parquet",
        "causal_labels_csv": dataset_dir / "causal_labels.csv",
        "causal_labels_parquet": dataset_dir / "causal_labels.parquet",
        "metadata": dataset_dir / "metadata.json",
        "provenance": dataset_dir / "provenance.json",
    }
    scientific.to_csv(paths["scientific_records_csv"], index=False)
    scientific.to_parquet(paths["scientific_records_parquet"], index=False)
    features.to_csv(paths["observable_features_csv"], index=False)
    features.to_parquet(paths["observable_features_parquet"], index=False)
    labels.to_csv(paths["causal_labels_csv"], index=False)
    labels.to_parquet(paths["causal_labels_parquet"], index=False)

    metadata = {
        "dataset_id": config.dataset_id,
        "schema_version": config.schema_version,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit_sha": current_git_sha(),
        "config": config.to_dict(),
        "config_sha256": config.config_hash(),
        "baseline_dataset": {
            "dataset_id": "ic_causal_agents_final_v1",
            "tag": "ic-2026-final",
            "commit": "57d32097414b9ec7def6d848e4f06499f1cd4199",
        },
        "number_of_samples": len(samples),
        "number_of_agent_families": len(
            {sample.agent_model_id for sample in samples}
        ),
        "agent_families": sorted(
            {sample.agent_model_id for sample in samples}
        ),
        "rejected_samples": 0,
        "deterministic_dataset": True,
        "random_seed": None,
        "feature_policy": (
            "observable_features contains process/state quantities only; agent IDs, "
            "physical-source labels, causal mechanisms, physical-regime labels and "
            "model-specific simulator parameters are excluded."
        ),
        "ground_truth_policy": (
            "Exact simulated density matrices and physical parameters remain in "
            "scientific_records, not observable_features."
        ),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "pandas": pd.__version__,
        },
    }
    paths["metadata"].write_text(
        json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8"
    )
    paths["provenance"].write_text(
        json.dumps(
            registry.to_dict(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return paths
