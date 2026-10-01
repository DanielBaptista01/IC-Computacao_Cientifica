"""Dataset export with explicit separation of observables, labels and metadata."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import pandas as pd
import scipy

from ic_quantum.core.probes import STANDARD_PROBE_KETS
from ic_quantum.data.causal_agent_schema import CausalAgentSampleRecord
from ic_quantum.data.scale_protocol import ScaledDatasetConfig


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unresolved"


def _input_bloch(probe_id: str) -> tuple[float, float, float]:
    ket = STANDARD_PROBE_KETS[probe_id]
    a, b = ket
    return (
        float(2.0 * np.real(np.conjugate(a) * b)),
        float(2.0 * np.imag(np.conjugate(a) * b)),
        float(np.abs(a) ** 2 - np.abs(b) ** 2),
    )


def _feature_row(row_id: int, sample: CausalAgentSampleRecord) -> dict[str, Any]:
    metrics = sample.signature.informational_metrics
    obs = sample.signature.observables
    spectrum = sorted(float(value) for value in sample.signature.spectrum)
    ix, iy, iz = _input_bloch(sample.initial_system_state)
    return {
        "row_id": row_id,
        "time_s": sample.time,
        "input_bloch_x": ix,
        "input_bloch_y": iy,
        "input_bloch_z": iz,
        "output_bloch_x": obs["X"],
        "output_bloch_y": obs["Y"],
        "output_bloch_z": obs["Z"],
        "entropy_after": metrics["entropy_after"],
        "delta_entropy": metrics["delta_entropy"],
        "purity_after": metrics["purity_after"],
        "delta_purity": metrics["delta_purity"],
        "coherence_l1_after": metrics["coherence_l1_after"],
        "delta_coherence_l1": metrics["delta_coherence_l1"],
        "fidelity_to_input": metrics["fidelity_to_input"],
        "state_eigenvalue_min": spectrum[0],
        "state_eigenvalue_max": spectrum[-1],
    }


def export_scientific_dataset(
    samples: list[CausalAgentSampleRecord],
    config: ScaledDatasetConfig,
    output_dir: Path,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    full_rows: list[dict[str, Any]] = []
    feature_rows: list[dict[str, Any]] = []
    label_rows: list[dict[str, Any]] = []

    for row_id, sample in enumerate(samples):
        feature_rows.append(_feature_row(row_id, sample))
        label_rows.append(
            {
                "row_id": row_id,
                "agent_model_id": sample.agent_model_id,
            }
        )
        full_rows.append(
            {
                "row_id": row_id,
                "sample_id": sample.sample_id,
                "agent_model_id": sample.agent_model_id,
                "initial_system_state": sample.initial_system_state,
                "time_s": sample.time,
                "parameter_values_json": json.dumps(
                    sample.parameter_values, sort_keys=True
                ),
                "signature_json": json.dumps(asdict(sample.signature), sort_keys=True),
                "metadata_json": json.dumps(sample.metadata, sort_keys=True),
                "random_seed": sample.random_seed,
            }
        )

    paths = {
        "samples": output_dir / "validated_samples.csv",
        "features": output_dir / "observable_features.csv",
        "labels": output_dir / "labels.csv",
        "metadata": output_dir / "dataset_metadata.json",
    }
    pd.DataFrame(full_rows).to_csv(paths["samples"], index=False)
    pd.DataFrame(feature_rows).to_csv(paths["features"], index=False)
    pd.DataFrame(label_rows).to_csv(paths["labels"], index=False)

    metadata = {
        "dataset_id": config.dataset_id,
        "schema_version": config.schema_version,
        "config": config.to_dict(),
        "config_sha256": config.config_hash(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit_sha": _git_sha(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "dependencies": {
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "pandas": pd.__version__,
        },
        "number_of_samples": len(samples),
        "number_of_agent_families": len({s.agent_model_id for s in samples}),
        "agent_families": sorted({s.agent_model_id for s in samples}),
        "deterministic": True,
        "random_seed": None,
        "feature_policy": (
            "observable_features.csv excludes causal labels, source/channel names and "
            "simulator rate parameters; labels.csv is stored separately."
        ),
    }
    paths["metadata"].write_text(
        json.dumps(metadata, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return paths
