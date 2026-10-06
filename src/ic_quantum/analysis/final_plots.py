"""Automatically generated figures for the IC final evidence package."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _save(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_temporal_metric(representative, metric: str, ylabel: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    for agent, frame in representative.groupby("agent_model_id"):
        ordered = frame.sort_values("time_s")
        ax.plot(ordered["time_s"], ordered[metric], label=agent)
    ax.set_xlabel("time (s)")
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.25)
    _save(fig, path)


def plot_matrix(frame: pd.DataFrame, title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    values = frame.to_numpy(dtype=float)
    image = ax.imshow(values)
    ax.set_xticks(range(len(frame.columns)), frame.columns, rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(frame.index)), frame.index, fontsize=7)
    ax.set_title(title)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            ax.text(j, i, f"{values[i,j]:.3f}", ha="center", va="center", fontsize=7)
    fig.colorbar(image, ax=ax)
    _save(fig, path)


def plot_reversibility(summary: pd.DataFrame, path: Path) -> None:
    pivot = summary.pivot(
        index="agent_model_id",
        columns="reversibility_class",
        values="condition_count",
    ).fillna(0)
    fig, ax = plt.subplots(figsize=(9, 5))
    pivot.plot(kind="bar", ax=ax)
    ax.set_ylabel("parameter-time conditions")
    ax.set_xlabel("causal-agent family")
    ax.tick_params(axis="x", labelrotation=35)
    ax.legend(fontsize=7)
    _save(fig, path)


def plot_probe_identifiability(probe_summary: pd.DataFrame, path: Path) -> None:
    aggregated = (
        probe_summary.groupby("probe_id", as_index=False)
        .agg(
            mean_min_trace_distance=("mean_min_trace_distance", "mean"),
            mean_collision_fraction=("collision_condition_fraction", "mean"),
        )
        .sort_values("probe_id")
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    positions = np.arange(len(aggregated))
    ax.bar(positions, aggregated["mean_min_trace_distance"])
    ax.set_xticks(positions, aggregated["probe_id"], rotation=45, ha="right")
    ax.set_ylabel("mean pairwise minimum trace distance")
    ax.set_xlabel("probe state")
    _save(fig, path)


def plot_intra_inter(intra_summary, pair_summary, path: Path) -> None:
    labels = list(intra_summary["agent_model_id"]) + ["inter-agent pairs"]
    values = list(intra_summary["mean_trace_distance"]) + [
        float(pair_summary["global_mean_trace_distance"].mean())
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(range(len(labels)), values)
    ax.set_xticks(range(len(labels)), labels, rotation=35, ha="right")
    ax.set_ylabel("mean trace distance")
    _save(fig, path)


def plot_sample_counts(sample_counts, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(sample_counts["agent_model_id"], sample_counts["sample_count"])
    ax.set_ylabel("valid samples")
    ax.tick_params(axis="x", labelrotation=35)
    _save(fig, path)


def generate_final_plots(
    *,
    representative,
    identifiability_matrix,
    collision_matrix,
    reversibility_summary,
    probe_summary,
    intra_summary,
    pair_summary,
    sample_counts,
    output_dir: Path,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    metric_specs = [
        ("entropy_after", "von Neumann entropy", "entropy_temporal.png"),
        ("purity_after", "purity", "purity_temporal.png"),
        ("coherence_l1_after", "l1 coherence", "coherence_temporal.png"),
        ("fidelity_to_input", "fidelity to input", "fidelity_temporal.png"),
        ("trace_distance_to_input", "trace distance to input", "trace_distance_temporal.png"),
    ]
    for metric, ylabel, name in metric_specs:
        path = output_dir / name
        plot_temporal_metric(representative, metric, ylabel, path)
        paths.append(path)

    path = output_dir / "identifiability_mean_min_distance_matrix.png"
    plot_matrix(identifiability_matrix, "Mean minimum trace distance", path)
    paths.append(path)
    path = output_dir / "identifiability_collision_fraction_matrix.png"
    plot_matrix(collision_matrix, "Collision-condition fraction", path)
    paths.append(path)
    path = output_dir / "reversibility_distribution.png"
    plot_reversibility(reversibility_summary, path)
    paths.append(path)
    path = output_dir / "probe_identifiability.png"
    plot_probe_identifiability(probe_summary, path)
    paths.append(path)
    path = output_dir / "intra_vs_inter_trace_distance.png"
    plot_intra_inter(intra_summary, pair_summary, path)
    paths.append(path)
    path = output_dir / "sample_counts_by_agent.png"
    plot_sample_counts(sample_counts, path)
    paths.append(path)
    return paths
