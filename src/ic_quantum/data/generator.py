"""Explicit generators for validated causal-agent samples.

This module produces deterministic model samples only. It does not train models and
keeps causal labels/metadata separate from future observable feature tables.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from ic_quantum.channels.amplitude_damping import amplitude_damping_kraus
from ic_quantum.channels.unitary import coherent_z_unitary
from ic_quantum.core.operators import SIGMA_X, SIGMA_Y, SIGMA_Z
from ic_quantum.core.probes import standard_probe_densities
from ic_quantum.data.causal_agent_schema import CausalAgentSampleRecord, CausalSignature
from ic_quantum.data.initial_catalog import build_initial_registry
from ic_quantum.data.scale_protocol import ScaledDatasetConfig
from ic_quantum.data.state_encoding import encode_complex_matrix
from ic_quantum.data.validator import validate_sample_record
from ic_quantum.dynamics.closed_system import apply_unitary
from ic_quantum.dynamics.microscopic import (
    exchange_amplitude_damping_probability,
    reduced_exchange_dynamics,
)
from ic_quantum.dynamics.reversibility import (
    assess_kraus_reversibility,
    assess_unitary_reversibility,
)
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


def _assessment_payload(assessment) -> dict[str, object]:
    return {
        "is_cptp": assessment.is_cptp,
        "linear_invertible": assessment.linear_invertible,
        "inverse_cptp": assessment.inverse_cptp,
        "direct_unitary_inverse": assessment.direct_unitary_inverse,
        "choi_rank": assessment.choi_rank,
        "condition_number": assessment.condition_number,
        "reversibility_class": assessment.classification,
    }


def build_signature(
    rho_before: np.ndarray,
    rho_after: np.ndarray,
    *,
    time: float,
    channel_descriptors: dict[str, object] | None = None,
) -> CausalSignature:
    """Construct an observable/inferable signature and preserve exact simulator state."""
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
        channel_descriptors=dict(channel_descriptors or {}),
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
        extra={"simulated_density_matrix": encode_complex_matrix(rho_after)},
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
    detuning = float(detuning)

    for time in times:
        t = float(time)
        unitary = coherent_z_unitary(omega=detuning, time=t)
        assessment = _assessment_payload(assess_unitary_reversibility(unitary))
        for probe_id, rho in _selected_probes(probe_ids).items():
            after = apply_unitary(rho, unitary)
            sample = CausalAgentSampleRecord(
                sample_id=(
                    f"{model.agent_id}__dw{detuning:.12g}__{probe_id}__t{t:.12g}"
                ),
                agent_model_id=model.agent_id,
                parameter_values={
                    "delta_omega": detuning,
                    "interaction_time": t,
                },
                time=t,
                initial_system_state=probe_id,
                signature=build_signature(
                    rho, after, time=t, channel_descriptors=assessment
                ),
                random_seed=None,
                metadata={
                    "deterministic": True,
                    "rate_value_rad_s": detuning,
                    "rate_parameter": "delta_omega",
                    "representation_origin": "unitary_hamiltonian",
                },
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
    coupling = float(coupling)

    for time in times:
        t = float(time)
        probability = exchange_amplitude_damping_probability(coupling, t)
        assessment = _assessment_payload(
            assess_kraus_reversibility(amplitude_damping_kraus(probability))
        )
        assessment["amplitude_damping_probability"] = probability
        for probe_id, rho in _selected_probes(probe_ids).items():
            after = reduced_exchange_dynamics(rho, coupling=coupling, time=t)
            sample = CausalAgentSampleRecord(
                sample_id=f"{model.agent_id}__g{coupling:.12g}__{probe_id}__t{t:.12g}",
                agent_model_id=model.agent_id,
                parameter_values={
                    "coupling": coupling,
                    "interaction_time": t,
                },
                time=t,
                initial_system_state=probe_id,
                signature=build_signature(
                    rho, after, time=t, channel_descriptors=assessment
                ),
                random_seed=None,
                metadata={
                    "deterministic": True,
                    "rate_value_rad_s": coupling,
                    "rate_parameter": "coupling",
                    "representation_origin": "joint_unitary_partial_trace",
                },
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


def generate_scaled_first_lot_samples(
    config: ScaledDatasetConfig,
) -> list[CausalAgentSampleRecord]:
    """Generate the first systematic, validated dataset for the two LEVEL_3 models."""
    samples: list[CausalAgentSampleRecord] = []
    for rate in config.rate_values_rad_s:
        samples.extend(
            generate_coherent_detuning_samples(
                detuning=rate,
                times=config.time_values_s,
                probe_ids=config.probe_ids,
            )
        )
        samples.extend(
            generate_exchange_relaxation_samples(
                coupling=rate,
                times=config.time_values_s,
                probe_ids=config.probe_ids,
            )
        )
    return samples
