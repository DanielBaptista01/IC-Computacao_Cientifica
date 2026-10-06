"""Generation of the frozen four-family IC final dataset."""

from __future__ import annotations

from itertools import product

from ic_quantum.channels.amplitude_damping import amplitude_damping_kraus
from ic_quantum.core.probes import final_probe_densities
from ic_quantum.data.causal_agent_schema import CausalAgentSampleRecord
from ic_quantum.data.channel_descriptors import (
    describe_kraus_channel,
    describe_unitary_channel,
)
from ic_quantum.data.final_catalog import build_final_registry
from ic_quantum.data.final_protocol import FinalDatasetConfig
from ic_quantum.data.generator import build_signature
from ic_quantum.data.validator import validate_sample_record
from ic_quantum.channels.unitary import coherent_z_unitary
from ic_quantum.dynamics.closed_system import apply_unitary
from ic_quantum.dynamics.markovian_reservoir import (
    apply_markovian_photon_reservoir_decay,
    markovian_decay_probability,
)
from ic_quantum.dynamics.microscopic import (
    exchange_amplitude_damping_probability,
    reduced_exchange_dynamics,
)
from ic_quantum.dynamics.spin_boson import (
    apply_finite_mode_spin_boson_dephasing,
    finite_mode_coherence_factor,
    finite_mode_dephasing_exponent,
    spin_boson_dephasing_kraus,
)


def _probes(config: FinalDatasetConfig):
    all_probes = final_probe_densities()
    return {probe_id: all_probes[probe_id] for probe_id in config.probe_ids}


def _finalize_sample(
    sample: CausalAgentSampleRecord,
    *,
    model,
) -> CausalAgentSampleRecord:
    validate_sample_record(sample, model)
    return sample


def generate_final_dataset_samples(config: FinalDatasetConfig) -> list[CausalAgentSampleRecord]:
    registry = build_final_registry()
    probes = _probes(config)
    samples: list[CausalAgentSampleRecord] = []

    coherent_model = registry.get("coherent-longitudinal-detuning")
    for p_index, rate in enumerate(config.coherent_detuning_rates):
        parameter_point_id = f"coherent_rate_{p_index:02d}"
        for t in config.time_values_s:
            unitary = coherent_z_unitary(omega=rate, time=t)
            channel_desc, choi_desc = describe_unitary_channel(unitary)
            for probe_id, rho in probes.items():
                after = apply_unitary(rho, unitary)
                samples.append(
                    _finalize_sample(
                        CausalAgentSampleRecord(
                            sample_id=(
                                f"{coherent_model.agent_id}__p{p_index:02d}"
                                f"__{probe_id}__t{t:.12g}"
                            ),
                            agent_model_id=coherent_model.agent_id,
                            parameter_values={
                                "delta_omega": float(rate),
                                "interaction_time": float(t),
                            },
                            time=float(t),
                            initial_system_state=probe_id,
                            signature=build_signature(
                                rho,
                                after,
                                time=t,
                                channel_descriptors=channel_desc,
                                choi_descriptors=choi_desc,
                            ),
                            random_seed=None,
                            metadata={
                                "deterministic": True,
                                "parameter_point_id": parameter_point_id,
                                "representation_origin": "unitary_hamiltonian",
                            },
                        ),
                        model=coherent_model,
                    )
                )

    exchange_model = registry.get("finite-two-level-exchange-relaxation")
    for p_index, coupling in enumerate(config.finite_exchange_couplings):
        parameter_point_id = f"exchange_rate_{p_index:02d}"
        for t in config.time_values_s:
            probability = exchange_amplitude_damping_probability(coupling, t)
            kraus = amplitude_damping_kraus(probability)
            channel_desc, choi_desc = describe_kraus_channel(kraus)
            for probe_id, rho in probes.items():
                after = reduced_exchange_dynamics(rho, coupling=coupling, time=t)
                samples.append(
                    _finalize_sample(
                        CausalAgentSampleRecord(
                            sample_id=(
                                f"{exchange_model.agent_id}__p{p_index:02d}"
                                f"__{probe_id}__t{t:.12g}"
                            ),
                            agent_model_id=exchange_model.agent_id,
                            parameter_values={
                                "coupling": float(coupling),
                                "interaction_time": float(t),
                            },
                            time=float(t),
                            initial_system_state=probe_id,
                            signature=build_signature(
                                rho,
                                after,
                                time=t,
                                channel_descriptors=channel_desc,
                                choi_descriptors=choi_desc,
                            ),
                            random_seed=None,
                            metadata={
                                "deterministic": True,
                                "parameter_point_id": parameter_point_id,
                                "representation_origin": "joint_unitary_partial_trace",
                                "effective_amplitude_damping_probability": probability,
                            },
                        ),
                        model=exchange_model,
                    )
                )

    photon_model = registry.get("markovian-photon-reservoir-decay")
    for p_index, decay_rate in enumerate(config.photon_decay_rates):
        parameter_point_id = f"photon_decay_{p_index:02d}"
        for t in config.time_values_s:
            probability = markovian_decay_probability(decay_rate, t)
            kraus = amplitude_damping_kraus(probability)
            channel_desc, choi_desc = describe_kraus_channel(kraus)
            for probe_id, rho in probes.items():
                after = apply_markovian_photon_reservoir_decay(
                    rho, decay_rate=decay_rate, time=t
                )
                samples.append(
                    _finalize_sample(
                        CausalAgentSampleRecord(
                            sample_id=(
                                f"{photon_model.agent_id}__p{p_index:02d}"
                                f"__{probe_id}__t{t:.12g}"
                            ),
                            agent_model_id=photon_model.agent_id,
                            parameter_values={
                                "decay_rate": float(decay_rate),
                                "interaction_time": float(t),
                            },
                            time=float(t),
                            initial_system_state=probe_id,
                            signature=build_signature(
                                rho,
                                after,
                                time=t,
                                channel_descriptors=channel_desc,
                                choi_descriptors=choi_desc,
                            ),
                            random_seed=None,
                            metadata={
                                "deterministic": True,
                                "parameter_point_id": parameter_point_id,
                                "representation_origin": "markovian_master_equation",
                                "effective_amplitude_damping_probability": probability,
                            },
                        ),
                        model=photon_model,
                    )
                )

    spin_model = registry.get("finite-mode-spin-boson-dephasing")
    spin_grid = product(
        config.spin_boson_mode_counts,
        config.spin_boson_cutoffs,
        config.spin_boson_temperature_ratios,
    )
    for p_index, (mode_count, cutoff, temperature_ratio) in enumerate(spin_grid):
        temperature = temperature_ratio * cutoff
        parameter_point_id = f"spin_boson_{p_index:02d}"
        for t in config.time_values_s:
            exponent = finite_mode_dephasing_exponent(
                time=t,
                mode_count=mode_count,
                cutoff_angular_frequency=cutoff,
                temperature_angular_frequency=temperature,
            )
            q = finite_mode_coherence_factor(
                time=t,
                mode_count=mode_count,
                cutoff_angular_frequency=cutoff,
                temperature_angular_frequency=temperature,
            )
            kraus = spin_boson_dephasing_kraus(q)
            channel_desc, choi_desc = describe_kraus_channel(kraus)
            channel_desc["analytical_linear_invertible"] = True
            channel_desc["numerical_linear_invertible_at_tolerance"] = bool(
                channel_desc["linear_invertible"]
            )
            channel_desc["coherence_factor"] = q
            channel_desc["dephasing_exponent"] = exponent
            if (
                not channel_desc["direct_unitary_inverse"]
                and not channel_desc["linear_invertible"]
            ):
                channel_desc["reversibility_class"] = (
                    "class_II_analytically_invertible_"
                    "numerically_effectively_singular_without_CPTP_inverse"
                )
                channel_desc["analytical_inverse_cptp"] = False
            for probe_id, rho in probes.items():
                after = apply_finite_mode_spin_boson_dephasing(
                    rho,
                    time=t,
                    mode_count=mode_count,
                    cutoff_angular_frequency=cutoff,
                    temperature_angular_frequency=temperature,
                )
                samples.append(
                    _finalize_sample(
                        CausalAgentSampleRecord(
                            sample_id=(
                                f"{spin_model.agent_id}__p{p_index:02d}"
                                f"__{probe_id}__t{t:.12g}"
                            ),
                            agent_model_id=spin_model.agent_id,
                            parameter_values={
                                "mode_count": int(mode_count),
                                "cutoff_angular_frequency": float(cutoff),
                                "temperature_angular_frequency": float(temperature),
                                "interaction_time": float(t),
                            },
                            time=float(t),
                            initial_system_state=probe_id,
                            signature=build_signature(
                                rho,
                                after,
                                time=t,
                                channel_descriptors=channel_desc,
                                choi_descriptors=choi_desc,
                            ),
                            random_seed=None,
                            metadata={
                                "deterministic": True,
                                "parameter_point_id": parameter_point_id,
                                "representation_origin": "exact_spin_boson_reduced_map",
                                "temperature_ratio": float(temperature_ratio),
                                "effective_coherence_factor": q,
                            },
                        ),
                        model=spin_model,
                    )
                )

    if len(samples) != config.expected_sample_count:
        raise RuntimeError(
            f"Generated {len(samples)} samples; expected {config.expected_sample_count}."
        )
    return samples
