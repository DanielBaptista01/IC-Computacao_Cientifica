"""Small, explicit sample generator for the first causal-agent lot.

This module intentionally generates only controlled smoke datasets. It does not
perform large sweeps and it does not expose causal IDs or simulator parameters as
default ML features.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from ic_quantum.channels.unitary import coherent_z_unitary
from ic_quantum.core.operators import SIGMA_X, SIGMA_Y, SIGMA_Z
from ic_quantum.core.probes import standard_probe_densities
from ic_quantum.data.causal_agent_schema import CausalAgentSampleRecord, CausalSignature
from ic_quantum.data.initial_catalog import build_initial_registry
from ic_quantum.data.validator import validate_sample_record
from ic_quantum.dynamics.closed_system import apply_unitary
from ic_quantum.dynamics.microscopic import reduced_exchange_dynamics
from ic_quantum.metrics.coherence import l1_coherence
from ic_quantum.metrics.entropy import von_neumann_entropy
from ic_quantum.metrics.fidelity import fidelity
from ic_quantum.metrics.purity import purity


def bloch_observables(rho: np.ndarray) -> dict[str, float]:
    """Return <X>, <Y>, <Z> for a one-qubit state."""
    return {
        "X": float(np.real(np.trace(rho @ SIGMA_X))),
        "Y": float(np.real(np.trace(rho @ SIGMA_Y))),
        "Z": float(np.real(np.trace(rho @ SIGMA_Z))),
    }


def build_signature(
    rho_before: np.ndarray,
    rho_after: np.ndarray,
    *,
    time: float,
) -> CausalSignature:
    """Construct a first observable signature without causal labels."""
    entropy_before = von_neumann_entropy(rho_before)
    entropy_after = von_neumann_entropy(rho_after)
    purity_before = purity(rho_before)
    purity_after = purity(rho_after)
    coherence_before = l1_coherence(rho_before)
    coherence_after = l1_coherence(rho_after)
    eigenvalues = np.linalg.eigvalsh(
        0.5 * (rho_after + rho_after.conjugate().T)
    ).real

    return CausalSignature(
        temporal_response={"time": float(time)},
        informational_metrics={
            "entropy_before": entropy_before,
            "entropy_after": entropy_after,
            "delta_entropy": entropy_after - entropy_before,
            "purity_before": purity_before,
            "purity_after": purity_after,
            "delta_purity": purity_after - purity_before,
            "coherence_l1_before": coherence_before,
            "coherence_l1_after": coherence_after,
            "delta_coherence_l1": coherence_after - coherence_before,
            "fidelity_to_input": fidelity(rho_before, rho_after),
        },
        observables=bloch_observables(rho_after),
        spectrum=[float(v) for v in eigenvalues],
    )


def _selected_probes(probe_ids: Iterable[str] | None) -> dict[str, np.ndarray]:
    probes = standard_probe_densities()
    if probe_ids is None:
        return probes
    selected: dict[str, np.ndarray] = {}
    for probe_id in probe_ids:
        try:
            selected[probe_id] = probes[probe_id]
        except KeyError as exc:
            raise ValueError(f"Unknown standardized probe: {probe_id!r}.") from exc
    return selected


def generate_coherent_detuning_samples(
    *,
    detuning: float,
    times: Iterable[float],
    probe_ids: Iterable[str] | None = None,
) -> list[CausalAgentSampleRecord]:
    registry = build_initial_registry()
    model = registry.get("coherent-longitudinal-detuning")
    samples: list[CausalAgentSampleRecord] = []

    for time in times:
        t = float(time)
        for probe_id, rho in _selected_probes(probe_ids).items():
            after = apply_unitary(
                rho,
                coherent_z_unitary(omega=float(detuning), time=t),
            )
            sample = CausalAgentSampleRecord(
                sample_id=f"{model.agent_id}__{probe_id}__t{t:.12g}",
                agent_model_id=model.agent_id,
                parameter_values={
                    "delta_omega": float(detuning),
                    "interaction_time": t,
                },
                time=t,
                initial_system_state=probe_id,
                signature=build_signature(rho, after, time=t),
                random_seed=None,
                metadata={"deterministic": True},
            )
            validate_sample_record(sample, model)
            samples.append(sample)
    return samples


def generate_exchange_relaxation_samples(
    *,
    coupling: float,
    times: Iterable[float],
    probe_ids: Iterable[str] | None = None,
) -> list[CausalAgentSampleRecord]:
    registry = build_initial_registry()
    model = registry.get("finite-two-level-exchange-relaxation")
    samples: list[CausalAgentSampleRecord] = []

    for time in times:
        t = float(time)
        for probe_id, rho in _selected_probes(probe_ids).items():
            after = reduced_exchange_dynamics(
                rho,
                coupling=float(coupling),
                time=t,
            )
            sample = CausalAgentSampleRecord(
                sample_id=f"{model.agent_id}__{probe_id}__t{t:.12g}",
                agent_model_id=model.agent_id,
                parameter_values={
                    "coupling": float(coupling),
                    "interaction_time": t,
                },
                time=t,
                initial_system_state=probe_id,
                signature=build_signature(rho, after, time=t),
                random_seed=None,
                metadata={"deterministic": True},
            )
            validate_sample_record(sample, model)
            samples.append(sample)
    return samples


def generate_first_lot_smoke_samples() -> list[CausalAgentSampleRecord]:
    """Return a deliberately tiny validation corpus, not a training dataset."""
    return [
        *generate_coherent_detuning_samples(detuning=1.0, times=(0.0, 0.7)),
        *generate_exchange_relaxation_samples(coupling=0.4, times=(0.0, 0.7)),
    ]
