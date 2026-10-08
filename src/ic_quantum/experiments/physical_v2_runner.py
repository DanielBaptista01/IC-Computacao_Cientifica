"""One-command physical-source causal-agent v2 pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

import matplotlib.pyplot as plt
import pandas as pd

from ic_quantum.analysis.final_reversibility import analyze_reversibility
from ic_quantum.analysis.physical_v2_identifiability import (
    analyze_physical_signature_overlap,
    analyze_process_signature_overlap,
    dephasing_source_trajectory_comparison,
)
from ic_quantum.analysis.physical_v2_matched import (
    matched_em_thermal_dephasing_experiment,
)
from ic_quantum.analysis.triad import analyze_agent_noise_entropy
from ic_quantum.analysis.physical_v2_response import (
    summarize_dephasing_trajectory_shapes,
    summarize_thermal_characteristic_times,
)
from ic_quantum.data.physical_catalog import build_physical_source_registry
from ic_quantum.data.physical_v2_export import export_physical_v2_dataset
from ic_quantum.data.physical_v2_generator import generate_physical_v2_samples
from ic_quantum.data.physical_v2_protocol import load_physical_v2_config


def _write(
    frame: pd.DataFrame,
    path: Path,
    preserve_index: bool = False,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=preserve_index)
    exported = frame.reset_index() if preserve_index else frame
    exported.to_parquet(path.with_suffix(".parquet"), index=False)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _plots(
    output_dir: Path,
    overlap,
    dephasing,
    reversibility,
    sample_counts,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 7))
    matrix = overlap["physical_mean_nearest_distance_matrix"]
    image = ax.imshow(matrix.to_numpy(dtype=float), aspect="auto")
    ax.set_xticks(
        range(len(matrix.columns)), labels=matrix.columns, rotation=90
    )
    ax.set_yticks(range(len(matrix.index)), labels=matrix.index)
    ax.set_title("Mean nearest trace-distance between physical-source families")
    fig.colorbar(image, ax=ax)
    fig.tight_layout()
    fig.savefig(
        output_dir / "physical_identifiability_matrix.png", dpi=160
    )
    plt.close(fig)

    if "process_mean_nearest_distance_matrix" in overlap:
        process_matrix = overlap["process_mean_nearest_distance_matrix"]
        fig, ax = plt.subplots(figsize=(9, 7))
        image = ax.imshow(process_matrix.to_numpy(dtype=float), aspect="auto")
        ax.set_xticks(
            range(len(process_matrix.columns)),
            labels=process_matrix.columns,
            rotation=90,
        )
        ax.set_yticks(
            range(len(process_matrix.index)),
            labels=process_matrix.index,
        )
        ax.set_title("Multi-probe process-signature nearest distance")
        fig.colorbar(image, ax=ax)
        fig.tight_layout()
        fig.savefig(
            output_dir / "process_identifiability_matrix.png", dpi=160
        )
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    for agent, group in dephasing.groupby("agent_model_id"):
        ax.plot(
            group["normalized_time"],
            group["x_coherence_response"],
            label=agent,
        )
    ax.set_xlabel("Normalized source-specific time")
    ax.set_ylabel("<X> for |+> probe")
    ax.set_title("Representative dephasing-source trajectory shapes")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(
        output_dir / "dephasing_source_trajectories.png", dpi=160
    )
    plt.close(fig)

    pivot = reversibility.pivot(
        index="agent_model_id",
        columns="reversibility_class",
        values="condition_count",
    ).fillna(0)
    ax = pivot.plot(kind="bar", stacked=True, figsize=(10, 6))
    ax.set_ylabel("Dynamic conditions")
    ax.set_title("Reversibility classification by physical source")
    ax.legend(fontsize=6)
    ax.figure.tight_layout()
    ax.figure.savefig(
        output_dir / "physical_reversibility_distribution.png", dpi=160
    )
    plt.close(ax.figure)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(sample_counts["agent_model_id"], sample_counts["sample_count"])
    ax.tick_params(axis="x", rotation=90)
    ax.set_ylabel("Samples")
    ax.set_title("Physical-source v2 sample coverage")
    fig.tight_layout()
    fig.savefig(output_dir / "physical_sample_counts.png", dpi=160)
    plt.close(fig)


def run_physical_v2_pipeline(output_dir: Path, config) -> dict:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    for subdir in ("dataset", "tables", "figures", "evidence", "config"):
        (output_dir / subdir).mkdir(parents=True, exist_ok=True)

    (output_dir / "config" / "effective_config.json").write_text(
        json.dumps(config.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    samples = generate_physical_v2_samples(config)
    paths = export_physical_v2_dataset(samples, config, output_dir)
    metadata = json.loads(paths["metadata"].read_text(encoding="utf-8"))

    overlap = analyze_physical_signature_overlap(
        samples, atol=config.identifiability_atol
    )
    process_overlap = analyze_process_signature_overlap(
        samples, atol=config.identifiability_atol
    )
    matched_summary, matched_trajectory = (
        matched_em_thermal_dephasing_experiment(config)
    )
    dephasing = dephasing_source_trajectory_comparison(samples)
    dephasing_shapes = summarize_dephasing_trajectory_shapes(dephasing)
    thermal_response = summarize_thermal_characteristic_times(samples)
    rev_conditions, rev_summary = analyze_reversibility(samples)
    _, triad_summary = analyze_agent_noise_entropy(
        samples, atol=config.identifiability_atol
    )

    tables = output_dir / "tables"
    for name, frame in overlap.items():
        _write(
            frame,
            tables / f"{name}.csv",
            preserve_index=name.endswith("_matrix"),
        )
    for name, frame in process_overlap.items():
        _write(
            frame,
            tables / f"{name}.csv",
            preserve_index=name.endswith("_matrix"),
        )
    _write(
        matched_summary,
        tables / "matched_em_thermal_dephasing_summary.csv",
    )
    _write(
        matched_trajectory,
        tables / "matched_em_thermal_dephasing_trajectory.csv",
    )
    _write(dephasing, tables / "dephasing_source_trajectories.csv")
    _write(dephasing_shapes, tables / "dephasing_source_shape_summary.csv")
    _write(thermal_response, tables / "thermal_characteristic_times.csv")
    _write(
        rev_conditions,
        tables / "physical_reversibility_by_condition.csv",
    )
    _write(
        rev_summary,
        tables / "physical_reversibility_summary.csv",
    )
    _write(
        triad_summary,
        tables / "physical_agent_noise_entropy_summary.csv",
    )

    sample_counts = (
        pd.Series(
            [s.agent_model_id for s in samples], name="agent_model_id"
        )
        .value_counts()
        .rename_axis("agent_model_id")
        .reset_index(name="sample_count")
        .sort_values("agent_model_id")
    )
    _write(sample_counts, tables / "physical_sample_counts.csv")

    parameter_counts = (
        pd.DataFrame(
            [
                {
                    "agent_model_id": s.agent_model_id,
                    "parameter_point_id": s.metadata["parameter_point_id"],
                }
                for s in samples
            ]
        )
        .drop_duplicates()
        .groupby("agent_model_id", as_index=False)
        .size()
        .rename(columns={"size": "parameter_point_count"})
    )
    _write(
        parameter_counts,
        tables / "physical_parameter_coverage.csv",
    )

    plot_overlap = {**overlap, **process_overlap}
    _plots(
        output_dir / "figures",
        plot_overlap,
        dephasing,
        rev_summary,
        sample_counts,
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(
        matched_trajectory["normalized_time"],
        matched_trajectory["thermal_spin_boson_coherence"],
        label="thermal spin-boson",
    )
    ax.plot(
        matched_trajectory["normalized_time"],
        matched_trajectory["em_gaussian_coherence"],
        label="quasistatic EM field",
    )
    ax.set_xlabel("Normalized source-specific time")
    ax.set_ylabel("Coherence factor")
    ax.set_title("Matched endpoint, different physical dephasing trajectories")
    ax.legend()
    fig.tight_layout()
    fig.savefig(
        output_dir / "figures" / "matched_em_thermal_dephasing.png",
        dpi=160,
    )
    plt.close(fig)

    registry = build_physical_source_registry()
    source_status = []
    for agent_id in registry.list_ids():
        model = registry.get(agent_id)
        source_status.append(
            {
                "agent_model_id": agent_id,
                "physical_source": model.physical_source,
                "causal_mechanism": model.causal_mechanism,
                "maturity_level": model.maturity_level.value,
                "has_phenomenological_provenance": any(
                    ref.kind.value == "PHENOMENOLOGICAL"
                    for ref in model.references
                ),
            }
        )
    source_status_frame = pd.DataFrame(source_status)
    _write(source_status_frame, tables / "physical_source_status.csv")

    pair_summary = overlap["physical_pair_summary"]
    evidence = output_dir / "evidence"
    (evidence / "PHYSICAL_V2_SCIENTIFIC_RESULTS.md").write_text(
        f"""# PHYSICAL_V2_SCIENTIFIC_RESULTS

Dataset: {config.dataset_id}

This expansion quantifies nine explicit physical-source/mechanism families while
preserving the frozen mechanistic v1 baseline. No ML/QML is trained.

- Valid samples: {len(samples)}
- Physical-source/mechanism families: {len(registry.list_ids())}
- Pairwise source pairs: {len(pair_summary)}
- Multi-probe process pairs: {len(process_overlap["process_pair_summary"])}
- All source records are LEVEL_3 numerically validated within their stated domains.
- The ionizing-radiation family is explicitly phenomenological at the bridge
  from deposited radiation energy/geometry to the initial excess quasiparticle
  fraction.

## Epistemic result

The implementation supports the operational statement that particular physical
sources can be represented by distinct mechanisms and quantitative trajectories.
It does not establish universal source identifiability. Pairwise state-response
and multi-probe process-response tables preserve collisions and non-identifiability.

A controlled matched-source experiment explicitly constructs an electromagnetic
quasistatic-field source and a thermal spin-boson source that have the same
reduced pure-dephasing channel at one selected snapshot. Their normalized
trajectories are then compared away from that endpoint.

## External-field entropy control

The external-field family contains coherent Zeeman evolution and an ensemble
dephasing regime. Coherent samples provide physical-source examples in which a
state can be perturbed while von Neumann entropy remains unchanged to numerical
precision.
""",
        encoding="utf-8",
    )
    (evidence / "PHYSICAL_V2_LIMITATIONS.md").write_text(
        """# PHYSICAL_V2_LIMITATIONS

- The external-EM corpus contains a magnetic Zeeman family and a coherent
  near-resonant Rabi family. The latter uses an effective Rabi rate; a raw
  E-field/polarization/dipole-matrix-element calibration is not inferred for an
  unspecified platform.
- The thermal spin-boson grid uses the exact finite-mode model in natural units;
  it is not a calibration of a particular cryostat/device.
- Mechanical effects are represented by two distinct selected-mode mechanisms:
  excitation exchange and longitudinal displacement dephasing. Neither is a
  model of arbitrary package/chassis vibration.
- Ionizing radiation is event-conditioned. The simulation starts from an excess
  quasiparticle fraction and does not simulate particle transport,
  deposited-energy geometry, the full phonon cascade, or correlated multi-qubit
  propagation.
- The charge-noise family is one symmetric bistable fluctuator, not a full 1/f
  ensemble of defects.
- Exact density matrices are simulator ground truth, not directly measured
  hardware data.
- Parameter intervals are literature-informed/theoretical coverage grids unless
  explicitly identified as equations from the cited literature.
- No Machine Learning or Quantum Machine Learning is trained.
""",
        encoding="utf-8",
    )
    (evidence / "PHYSICAL_V2_IDENTIFIABILITY.md").write_text(
        """# PHYSICAL_V2_IDENTIFIABILITY

Sources operate on different physical time scales, so the primary pairwise
analysis does not equate the numerical value of elapsed time between unrelated
sources. For each source pair and probe state, it measures symmetric
nearest-neighbour trace distance over each source's sampled parameter/time
manifold.

The zero-time identity is retained as a real collision. A separate nonzero-time
minimum is also reported. This is a signature-overlap analysis, not proof that a
single reduced-state snapshot uniquely determines microscopic cause.

See the physical_pair_summary, physical_probe_overlap,
physical_mean_nearest_distance_matrix, process_pair_summary,
process_mean_nearest_distance_matrix, matched_em_thermal_dephasing_summary,
dephasing_source_trajectories and dephasing_source_shape_summary tables.

The process-response metric concatenates four linearly independent qubit probes
(0, 1, +, +i) and reports RMS trace distance across them. It is an operational
multi-probe metric, not a diamond norm.

For thermal sources, thermal_characteristic_times.csv reports first-passage
1/e scales T1* and T2*. They are descriptors of the sampled trajectory, not
assumed exponential constants; recurrent models may cross and later revive.
""",
        encoding="utf-8",
    )
    (evidence / "PHYSICAL_V2_REVERSIBILITY.md").write_text(
        """# PHYSICAL_V2_REVERSIBILITY

Reversibility is classified per parameter/time condition from the effective
reduced map. Coherent external-field conditions admit direct unitary inversion;
ensemble, thermal, mechanical, radiative, radiation-conditioned and
charge-fluctuator regimes may instead be nonunitary or only linearly invertible.

No claim of physical recoverability is inferred solely from a non-CPTP linear
inverse. See physical_reversibility_summary.csv.
""",
        encoding="utf-8",
    )

    summary = {
        "dataset_id": config.dataset_id,
        "git_commit_sha": metadata["git_commit_sha"],
        "config_sha256": config.config_hash(),
        "baseline_dataset": metadata["baseline_dataset"],
        "N_A": len(registry.list_ids()),
        "N_S": len(samples),
        "agent_sample_counts": dict(
            zip(
                sample_counts["agent_model_id"],
                sample_counts["sample_count"].astype(int),
            )
        ),
        "parameter_point_counts": dict(
            zip(
                parameter_counts["agent_model_id"],
                parameter_counts["parameter_point_count"].astype(int),
            )
        ),
        "pairwise_source_pairs": len(pair_summary),
        "process_pairwise_source_pairs": len(
            process_overlap["process_pair_summary"]
        ),
        "matched_dephasing_max_probe_trace_distance": float(
            matched_summary.iloc[0][
                "max_probe_trace_distance_at_matched_snapshot"
            ]
        ),
        "matched_dephasing_max_trajectory_difference": float(
            matched_summary.iloc[0][
                "max_normalized_trajectory_coherence_difference"
            ]
        ),
        "machine_learning_trained": False,
        "radiation_source_channel_bridge": "PHENOMENOLOGICAL",
        "epistemic_guard": (
            "Physical-source families are quantitatively modeled under stated "
            "assumptions; universal causal uniqueness is not claimed."
        ),
    }
    (output_dir / "PHYSICAL_V2_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    hashes = {}
    for path in sorted(output_dir.rglob("*")):
        if path.is_file() and path.name != "PHYSICAL_V2_MANIFEST.json":
            hashes[str(path.relative_to(output_dir))] = {
                "sha256": _sha(path),
                "size_bytes": path.stat().st_size,
            }
    (output_dir / "PHYSICAL_V2_MANIFEST.json").write_text(
        json.dumps(
            {
                "dataset_id": config.dataset_id,
                "git_commit_sha": metadata["git_commit_sha"],
                "config_sha256": config.config_hash(),
                "files": hashes,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="experiments/configs/ic_causal_agents_physical_v2.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/physical_v2"),
    )
    args = parser.parse_args()
    run_physical_v2_pipeline(
        args.output_dir,
        load_physical_v2_config(args.config),
    )


if __name__ == "__main__":
    main()
