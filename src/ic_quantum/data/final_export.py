"""Stable CSV/Parquet export for the IC final causal-agent dataset."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
import platform
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import pandas as pd
import scipy

from ic_quantum.core.operators import SIGMA_X, SIGMA_Y, SIGMA_Z
from ic_quantum.core.probes import final_probe_densities
from ic_quantum.data.causal_agent_schema import CausalAgentSampleRecord
from ic_quantum.data.final_catalog import build_final_registry
from ic_quantum.data.final_protocol import FinalDatasetConfig


def current_git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unresolved"


def _bloch(rho: np.ndarray) -> tuple[float, float, float]:
    return (
        float(np.real(np.trace(rho @ SIGMA_X))),
        float(np.real(np.trace(rho @ SIGMA_Y))),
        float(np.real(np.trace(rho @ SIGMA_Z))),
    )


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (np.floating, float)):
        numeric = float(value)
        return numeric if np.isfinite(numeric) else None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def _strict_json(value: Any) -> str:
    return json.dumps(_json_safe(value), sort_keys=True, allow_nan=False)


def _feature_row(row_id: int, sample: CausalAgentSampleRecord) -> dict[str, Any]:
    probe_rho = final_probe_densities()[sample.initial_system_state]
    ix, iy, iz = _bloch(probe_rho)
    metrics = sample.signature.informational_metrics
    obs = sample.signature.observables
    spectrum = sorted(float(v) for v in sample.signature.spectrum)
    channel = sample.signature.channel_descriptors
    choi = sample.signature.choi_descriptors
    choi_eigs = list(choi["choi_eigenvalues"])
    singular = list(choi["superoperator_singular_values"])
    return {
        "row_id": row_id,
        "time_s": float(sample.time),
        "input_bloch_x": ix,
        "input_bloch_y": iy,
        "input_bloch_z": iz,
        "output_bloch_x": float(obs["X"]),
        "output_bloch_y": float(obs["Y"]),
        "output_bloch_z": float(obs["Z"]),
        "entropy_after": float(metrics["entropy_after"]),
        "delta_entropy": float(metrics["delta_entropy"]),
        "purity_after": float(metrics["purity_after"]),
        "delta_purity": float(metrics["delta_purity"]),
        "coherence_l1_after": float(metrics["coherence_l1_after"]),
        "delta_coherence_l1": float(metrics["delta_coherence_l1"]),
        "fidelity_to_input": float(metrics["fidelity_to_input"]),
        "trace_distance_to_input": float(metrics["trace_distance_to_input"]),
        "state_eigenvalue_min": spectrum[0],
        "state_eigenvalue_max": spectrum[-1],
        "choi_rank": int(channel["choi_rank"]),
        "channel_linear_invertible": bool(channel["linear_invertible"]),
        "channel_direct_unitary_inverse": bool(channel["direct_unitary_inverse"]),
        "channel_condition_number": (
            None if channel["condition_number"] is None
            else float(channel["condition_number"])
        ),
        "normalized_choi_purity": float(choi["normalized_choi_purity"]),
        "superoperator_determinant_abs": float(
            choi["superoperator_determinant_abs"]
        ),
        "choi_eigenvalue_0": float(choi_eigs[0]),
        "choi_eigenvalue_1": float(choi_eigs[1]),
        "choi_eigenvalue_2": float(choi_eigs[2]),
        "choi_eigenvalue_3": float(choi_eigs[3]),
        "superoperator_singular_value_0": float(singular[0]),
        "superoperator_singular_value_1": float(singular[1]),
        "superoperator_singular_value_2": float(singular[2]),
        "superoperator_singular_value_3": float(singular[3]),
    }


def _scientific_row(
    row_id: int,
    sample: CausalAgentSampleRecord,
    model,
) -> dict[str, Any]:
    metrics = sample.signature.informational_metrics
    obs = sample.signature.observables
    return {
        "row_id": row_id,
        "sample_id": sample.sample_id,
        "agent_model_id": sample.agent_model_id,
        "agent_name": model.provisional_name,
        "physical_category": model.physical_category,
        "physical_description": model.physical_description,
        "maturity_level": model.maturity_level.value,
        "initial_system_state": sample.initial_system_state,
        "time_s": float(sample.time),
        "parameter_point_id": sample.metadata["parameter_point_id"],
        "parameter_values_json": _strict_json(sample.parameter_values),
        "density_matrix_json": _strict_json(
            sample.signature.extra["simulated_density_matrix"]
        ),
        "output_bloch_x": float(obs["X"]),
        "output_bloch_y": float(obs["Y"]),
        "output_bloch_z": float(obs["Z"]),
        "entropy_after": float(metrics["entropy_after"]),
        "delta_entropy": float(metrics["delta_entropy"]),
        "purity_after": float(metrics["purity_after"]),
        "delta_purity": float(metrics["delta_purity"]),
        "coherence_l1_after": float(metrics["coherence_l1_after"]),
        "delta_coherence_l1": float(metrics["delta_coherence_l1"]),
        "fidelity_to_input": float(metrics["fidelity_to_input"]),
        "trace_distance_to_input": float(metrics["trace_distance_to_input"]),
        "state_spectrum_json": _strict_json(sample.signature.spectrum),
        "channel_descriptors_json": _strict_json(
            sample.signature.channel_descriptors
        ),
        "choi_superoperator_descriptors_json": _strict_json(
            sample.signature.choi_descriptors
        ),
        "reversibility_class": sample.signature.channel_descriptors[
            "reversibility_class"
        ],
        "representation_origin": sample.metadata["representation_origin"],
        "random_seed": sample.random_seed,
        "metadata_json": _strict_json(sample.metadata),
    }


def export_final_dataset(
    samples: list[CausalAgentSampleRecord],
    config: FinalDatasetConfig,
    output_dir: Path,
) -> dict[str, Path]:
    dataset_dir = output_dir / "dataset"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    registry = build_final_registry()

    scientific_rows: list[dict[str, Any]] = []
    feature_rows: list[dict[str, Any]] = []
    label_rows: list[dict[str, Any]] = []

    for row_id, sample in enumerate(samples):
        model = registry.get(sample.agent_model_id)
        scientific_rows.append(_scientific_row(row_id, sample, model))
        feature_rows.append(_feature_row(row_id, sample))
        label_rows.append(
            {
                "row_id": row_id,
                "sample_id": sample.sample_id,
                "agent_model_id": sample.agent_model_id,
            }
        )

    scientific = pd.DataFrame(scientific_rows)
    features = pd.DataFrame(feature_rows)
    labels = pd.DataFrame(label_rows)

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
        "number_of_samples": len(samples),
        "number_of_agent_families": len({s.agent_model_id for s in samples}),
        "agent_families": sorted({s.agent_model_id for s in samples}),
        "validation_policy": (
            "fail-fast: any sample failing corpus/mathematical validation aborts generation"
        ),
        "rejected_samples": 0,
        "deterministic_dataset": True,
        "random_seed": None,
        "feature_policy": (
            "observable_features excludes agent/source/channel names, sample IDs and "
            "model-specific simulator parameters. Causal labels are stored separately."
        ),
        "ground_truth_policy": (
            "Exact simulated density matrices are retained only in scientific_records; "
            "they are simulator ground truth, not assumed directly measurable on hardware."
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
        json.dumps(registry.to_dict(), indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )
    return paths
