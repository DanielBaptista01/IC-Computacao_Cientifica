"""One-command final scientific pipeline for the 2026 IC."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pandas as pd

from ic_quantum.analysis.channel_collisions import exact_amplitude_damping_source_collision_table
from ic_quantum.analysis.final_evidence import write_final_evidence
from ic_quantum.analysis.final_identifiability import (
    analyze_intra_agent_variation,
    analyze_pairwise_identifiability,
)
from ic_quantum.analysis.final_plots import generate_final_plots
from ic_quantum.analysis.final_reversibility import analyze_reversibility
from ic_quantum.analysis.triad import analyze_agent_noise_entropy, representative_temporal_metrics
from ic_quantum.data.final_export import export_final_dataset
from ic_quantum.data.final_generator import generate_final_dataset_samples
from ic_quantum.data.final_protocol import load_final_dataset_config


def _write_frame(
    frame: pd.DataFrame,
    path: Path,
    parquet: bool = False,
    preserve_index: bool = False,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=preserve_index)
    if parquet:
        exported = frame.reset_index() if preserve_index else frame
        exported.to_parquet(path.with_suffix(".parquet"), index=False)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _runtime_freeze(path: Path) -> None:
    try:
        content = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    except (OSError, subprocess.CalledProcessError):
        content = "UNRESOLVED\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_final_pipeline(output_dir: Path, config) -> dict:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in ("config", "tables", "figures", "environment"):
        (output_dir / name).mkdir(parents=True, exist_ok=True)

    (output_dir / "config" / "effective_config.json").write_text(
        json.dumps(config.to_dict(), indent=2, sort_keys=True), encoding="utf-8"
    )
    _runtime_freeze(output_dir / "environment" / "requirements-freeze.txt")

    samples = generate_final_dataset_samples(config)
    dataset_paths = export_final_dataset(samples, config, output_dir)
    metadata = json.loads(dataset_paths["metadata"].read_text(encoding="utf-8"))

    ident = analyze_pairwise_identifiability(samples, atol=config.identifiability_atol)
    intra = analyze_intra_agent_variation(samples, atol=config.identifiability_atol)
    triad_frame, triad_summary = analyze_agent_noise_entropy(
        samples, atol=config.identifiability_atol
    )
    representative = representative_temporal_metrics(triad_frame)
    rev_conditions, rev_summary = analyze_reversibility(samples)
    collision_experiment = exact_amplitude_damping_source_collision_table()

    tables = output_dir / "tables"
    for name, frame in ident.items():
        _write_frame(
            frame,
            tables / f"{name}.csv",
            parquet=name in {"condition_pairwise", "collision_regions"},
            preserve_index=name in {
                "mean_min_distance_matrix",
                "collision_fraction_matrix",
            },
        )
    for name, frame in intra.items():
        _write_frame(frame, tables / f"{name}.csv")
    _write_frame(triad_summary, tables / "agent_noise_entropy_summary.csv")
    _write_frame(representative, tables / "representative_temporal_metrics.csv")
    _write_frame(rev_conditions, tables / "reversibility_by_condition.csv", parquet=True)
    _write_frame(rev_summary, tables / "reversibility_summary.csv")
    _write_frame(collision_experiment, tables / "source_channel_collision.csv")

    sample_counts = (
        pd.Series([sample.agent_model_id for sample in samples], name="agent_model_id")
        .value_counts()
        .rename_axis("agent_model_id")
        .reset_index(name="sample_count")
        .sort_values("agent_model_id")
        .reset_index(drop=True)
    )
    _write_frame(sample_counts, tables / "sample_counts.csv")

    parameter_counts = (
        pd.DataFrame(
            [
                {
                    "agent_model_id": sample.agent_model_id,
                    "parameter_point_id": sample.metadata["parameter_point_id"],
                }
                for sample in samples
            ]
        )
        .drop_duplicates()
        .groupby("agent_model_id", as_index=False)
        .size()
        .rename(columns={"size": "parameter_point_count"})
    )
    _write_frame(parameter_counts, tables / "parameter_coverage.csv")

    generate_final_plots(
        representative=representative,
        identifiability_matrix=ident["mean_min_distance_matrix"],
        collision_matrix=ident["collision_fraction_matrix"],
        reversibility_summary=rev_summary,
        probe_summary=ident["probe_summary"],
        intra_summary=intra["intra_summary"],
        pair_summary=ident["pair_summary"],
        sample_counts=sample_counts,
        output_dir=output_dir / "figures",
    )

    write_final_evidence(
        output_dir=output_dir,
        config=config,
        sample_counts=sample_counts,
        pair_summary=ident["pair_summary"],
        collision_regions=ident["collision_regions"],
        triad_summary=triad_summary,
        reversibility_summary=rev_summary,
        collision_experiment=collision_experiment,
        metadata=metadata,
    )

    summary = {
        "dataset_id": config.dataset_id,
        "git_commit_sha": metadata["git_commit_sha"],
        "config_sha256": config.config_hash(),
        "N_A": int(len(sample_counts)),
        "N_S": int(sample_counts["sample_count"].sum()),
        "rejected_samples": 0,
        "agent_sample_counts": dict(
            zip(sample_counts["agent_model_id"], sample_counts["sample_count"].astype(int))
        ),
        "parameter_point_counts": dict(
            zip(
                parameter_counts["agent_model_id"],
                parameter_counts["parameter_point_count"].astype(int),
            )
        ),
        "pairwise_agent_pairs": int(len(ident["pair_summary"])),
        "collision_regions": int(len(ident["collision_regions"])),
        "source_channel_collision_max_trace_distance": float(
            collision_experiment["max_trace_distance_across_probes"].max()
        ),
        "machine_learning_trained": False,
        "epistemic_guard": (
            "Conditional operational distinguishability only; no universal causal uniqueness."
        ),
    }
    (output_dir / "FINAL_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )

    hashed_files = {}
    for path in sorted(output_dir.rglob("*")):
        if path.is_file() and path.name != "FINAL_DATASET_MANIFEST.json":
            hashed_files[str(path.relative_to(output_dir))] = {
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
            }
    manifest = {
        "dataset_id": config.dataset_id,
        "git_commit_sha": metadata["git_commit_sha"],
        "config_sha256": config.config_hash(),
        "files": hashed_files,
    }
    (output_dir / "FINAL_DATASET_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="experiments/configs/ic_causal_agents_final_v1.json"
    )
    parser.add_argument("--output-dir", type=Path, default=Path("results/final"))
    args = parser.parse_args()
    run_final_pipeline(Path(args.output_dir), load_final_dataset_config(args.config))


if __name__ == "__main__":
    main()
