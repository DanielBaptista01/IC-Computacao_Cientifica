"""Generate the physical-source causal-agent dataset v2."""

from __future__ import annotations

from itertools import product

import numpy as np

from ic_quantum.core.probes import final_probe_densities
from ic_quantum.data.causal_agent_schema import CausalAgentSampleRecord
from ic_quantum.data.channel_descriptors import (
    describe_kraus_channel,
    describe_unitary_channel,
)
from ic_quantum.data.generator import build_signature
from ic_quantum.data.physical_catalog import build_physical_source_registry
from ic_quantum.data.physical_v2_protocol import PhysicalV2Config
from ic_quantum.data.validator import validate_sample_record
from ic_quantum.dynamics.charge_fluctuator import (
    random_telegraph_coherence_factor,
    random_telegraph_dephasing_kraus,
    random_telegraph_spectral_density,
)
from ic_quantum.dynamics.closed_system import apply_unitary
from ic_quantum.dynamics.electromagnetic_drive import em_drive_unitary
from ic_quantum.dynamics.external_field import (
    external_magnetic_field_unitary,
    gaussian_quasistatic_field_coherence_factor,
    gaussian_quasistatic_field_kraus,
)
from ic_quantum.dynamics.mechanical_phonon import (
    mechanical_phonon_kraus,
    thermal_mean_occupation,
)
from ic_quantum.dynamics.mechanical_mode import (
    mechanical_coherence_factor,
    mechanical_dephasing_exponent,
)
from ic_quantum.dynamics.open_system import apply_kraus
from ic_quantum.dynamics.radiation import (
    ionizing_radiation_kraus,
    quasiparticle_fraction_and_hazard,
)
from ic_quantum.dynamics.thermal_reservoir import (
    bose_occupation,
    generalized_amplitude_damping_kraus,
)
from ic_quantum.dynamics.spin_boson import (
    finite_mode_coherence_factor,
    finite_mode_dephasing_exponent,
    spin_boson_dephasing_kraus,
)


def _signature(
    rho,
    after,
    *,
    time: float,
    channel,
    choi,
    physical_parameters: dict,
    extra: dict | None = None,
):
    signature = build_signature(
        rho,
        after,
        time=time,
        channel_descriptors=channel,
        choi_descriptors=choi,
    )
    signature.physical_parameters = dict(physical_parameters)
    if extra:
        signature.extra.update(extra)
    return signature


def _sample(
    *,
    model,
    parameter_point_id: str,
    probe_id: str,
    rho,
    time: float,
    parameters: dict,
    channel,
    choi,
    after,
    representation_origin: str,
    physical_regime: str,
    extra: dict | None = None,
    numerical_metadata: dict | None = None,
) -> CausalAgentSampleRecord:
    sample = CausalAgentSampleRecord(
        sample_id=(
            f"{model.agent_id}__{parameter_point_id}__{probe_id}__t{time:.12g}"
        ),
        agent_model_id=model.agent_id,
        parameter_values=parameters,
        time=float(time),
        initial_system_state=probe_id,
        signature=_signature(
            rho,
            after,
            time=time,
            channel=channel,
            choi=choi,
            physical_parameters=parameters,
            extra=extra,
        ),
        random_seed=None,
        metadata={
            "deterministic": True,
            "parameter_point_id": parameter_point_id,
            "representation_origin": representation_origin,
            "physical_regime": physical_regime,
            **(numerical_metadata or {}),
        },
    )
    validate_sample_record(sample, model)
    return sample


def _orientation(name: str) -> tuple[float, float]:
    if name == "x":
        return np.pi / 2.0, 0.0
    if name == "z":
        return 0.0, 0.0
    raise ValueError(f"Unsupported EM orientation: {name!r}.")


def generate_physical_v2_samples(
    config: PhysicalV2Config,
) -> list[CausalAgentSampleRecord]:
    registry = build_physical_source_registry()
    all_probes = final_probe_densities()
    probes = {key: all_probes[key] for key in config.probe_ids}
    samples: list[CausalAgentSampleRecord] = []

    model = registry.get("external-magnetic-field-wave")
    pidx = 0
    for amplitude, frequency_hz, orientation in product(
        config.em_field_amplitudes_t,
        config.em_drive_frequencies_hz,
        config.em_orientations,
    ):
        theta, azimuth = _orientation(orientation)
        for time in config.em_times_s:
            parameters = {
                "gyromagnetic_ratio": config.em_gyromagnetic_ratio,
                "field_amplitude": float(amplitude),
                "field_standard_deviation": 0.0,
                "drive_angular_frequency": float(2.0 * np.pi * frequency_hz),
                "phase": 0.0,
                "polar_angle": float(theta),
                "azimuth_angle": float(azimuth),
                "interaction_time": float(time),
            }
            unitary = external_magnetic_field_unitary(
                gyromagnetic_ratio=parameters["gyromagnetic_ratio"],
                field_amplitude=parameters["field_amplitude"],
                drive_angular_frequency=parameters["drive_angular_frequency"],
                phase=parameters["phase"],
                polar_angle=parameters["polar_angle"],
                azimuth_angle=parameters["azimuth_angle"],
                time=time,
            )
            channel, choi = describe_unitary_channel(unitary)
            for probe_id, rho in probes.items():
                samples.append(
                    _sample(
                        model=model,
                        parameter_point_id=f"em_coherent_{pidx:03d}",
                        probe_id=probe_id,
                        rho=rho,
                        time=time,
                        parameters=parameters,
                        channel=channel,
                        choi=choi,
                        after=apply_unitary(rho, unitary),
                        representation_origin="semiclassical_zeeman_hamiltonian",
                        physical_regime="coherent_external_field",
                        extra={
                            "field_orientation": orientation,
                            "drive_frequency_hz": float(frequency_hz),
                        },
                    )
                )
        pidx += 1

    for sigma_b in config.em_gaussian_sigma_b_t:
        for time in config.em_times_s:
            parameters = {
                "gyromagnetic_ratio": config.em_gyromagnetic_ratio,
                "field_amplitude": 0.0,
                "field_standard_deviation": float(sigma_b),
                "drive_angular_frequency": 0.0,
                "phase": 0.0,
                "polar_angle": 0.0,
                "azimuth_angle": 0.0,
                "interaction_time": float(time),
            }
            kraus = gaussian_quasistatic_field_kraus(
                gyromagnetic_ratio=config.em_gyromagnetic_ratio,
                field_standard_deviation=sigma_b,
                time=time,
            )
            q = gaussian_quasistatic_field_coherence_factor(
                gyromagnetic_ratio=config.em_gyromagnetic_ratio,
                field_standard_deviation=sigma_b,
                time=time,
            )
            channel, choi = describe_kraus_channel(kraus)
            for probe_id, rho in probes.items():
                samples.append(
                    _sample(
                        model=model,
                        parameter_point_id=f"em_gaussian_{pidx:03d}",
                        probe_id=probe_id,
                        rho=rho,
                        time=time,
                        parameters=parameters,
                        channel=channel,
                        choi=choi,
                        after=apply_kraus(rho, kraus),
                        representation_origin="gaussian_quasistatic_field_ensemble",
                        physical_regime="stochastic_longitudinal_field",
                        extra={"coherence_factor": q},
                    )
                )
        pidx += 1


    # 2) Near-resonant coherent electromagnetic wave (effective Rabi coupling).
    model = registry.get("external-electromagnetic-rabi-drive")
    for pidx, (rabi_hz, detuning_hz, phase) in enumerate(
        product(
            config.rabi_rates_hz,
            config.rabi_detunings_hz,
            config.rabi_phases_rad,
        )
    ):
        rabi_rate = 2.0 * np.pi * rabi_hz
        detuning = 2.0 * np.pi * detuning_hz
        for time in config.rabi_times_s:
            parameters = {
                "rabi_rate": float(rabi_rate),
                "detuning": float(detuning),
                "phase": float(phase),
                "interaction_time": float(time),
            }
            unitary = em_drive_unitary(
                rabi_rate=rabi_rate,
                detuning=detuning,
                phase=phase,
                time=time,
            )
            channel, choi = describe_unitary_channel(unitary)
            for probe_id, rho in probes.items():
                samples.append(
                    _sample(
                        model=model,
                        parameter_point_id=f"em_rabi_{pidx:03d}",
                        probe_id=probe_id,
                        rho=rho,
                        time=time,
                        parameters=parameters,
                        channel=channel,
                        choi=choi,
                        after=apply_unitary(rho, unitary),
                        representation_origin="semiclassical_rotating_frame_RWA",
                        physical_regime="coherent_near_resonant_em_drive",
                        extra={
                            "rabi_rate_hz": float(rabi_hz),
                            "detuning_hz": float(detuning_hz),
                            "phase_rad": float(phase),
                        },
                    )
                )

    # 3) Finite thermal bosonic pure-dephasing source.
    model = registry.get("finite-mode-spin-boson-dephasing")
    for pidx, (mode_count, cutoff, ratio) in enumerate(
        product(
            config.thermal_mode_counts,
            config.thermal_cutoffs_rad_s,
            config.thermal_temperature_ratios,
        )
    ):
        temperature = ratio * cutoff
        for time in config.thermal_times_s:
            parameters = {
                "mode_count": int(mode_count),
                "cutoff_angular_frequency": float(cutoff),
                "temperature_angular_frequency": float(temperature),
                "interaction_time": float(time),
            }
            q = finite_mode_coherence_factor(
                time=time,
                mode_count=mode_count,
                cutoff_angular_frequency=cutoff,
                temperature_angular_frequency=temperature,
            )
            exponent = finite_mode_dephasing_exponent(
                time=time,
                mode_count=mode_count,
                cutoff_angular_frequency=cutoff,
                temperature_angular_frequency=temperature,
            )
            kraus = spin_boson_dephasing_kraus(q)
            channel, choi = describe_kraus_channel(kraus)
            channel["analytical_linear_invertible"] = True
            channel["numerical_linear_invertible_at_tolerance"] = bool(
                channel["linear_invertible"]
            )
            if (
                not channel["direct_unitary_inverse"]
                and not channel["linear_invertible"]
            ):
                channel["reversibility_class"] = (
                    "class_II_analytically_invertible_"
                    "numerically_effectively_singular_without_CPTP_inverse"
                )
                channel["analytical_inverse_cptp"] = False
            for probe_id, rho in probes.items():
                samples.append(
                    _sample(
                        model=model,
                        parameter_point_id=f"thermal_spin_boson_{pidx:03d}",
                        probe_id=probe_id,
                        rho=rho,
                        time=time,
                        parameters=parameters,
                        channel=channel,
                        choi=choi,
                        after=apply_kraus(rho, kraus),
                        representation_origin="exact_finite_spin_boson_map",
                        physical_regime="thermal_bosonic_dephasing",
                        extra={
                            "coherence_factor": q,
                            "dephasing_exponent": exponent,
                            "temperature_ratio": float(ratio),
                        },
                    )
                )

    # Zero-temperature radiative decay remains in frozen v1. In v2 it is
    # the T=0 limit of thermal-photon-reservoir and is not duplicated as a label.

    # 5) Finite-temperature electromagnetic photon reservoir.
    model = registry.get("thermal-photon-reservoir")
    transition_omega = (
        2.0 * np.pi * config.thermal_photon_transition_frequency_hz
    )
    for pidx, (decay_rate, temperature) in enumerate(
        product(
            config.thermal_photon_decay_rates_s,
            config.thermal_photon_temperatures_k,
        )
    ):
        nbar = bose_occupation(transition_omega, temperature)
        equilibrium_excited = nbar / (2.0 * nbar + 1.0)
        for time in config.thermal_photon_times_s:
            parameters = {
                "decay_rate": float(decay_rate),
                "transition_angular_frequency": float(transition_omega),
                "temperature_kelvin": float(temperature),
                "interaction_time": float(time),
            }
            kraus = generalized_amplitude_damping_kraus(
                decay_rate, nbar, time
            )
            channel, choi = describe_kraus_channel(kraus)
            for probe_id, rho in probes.items():
                samples.append(
                    _sample(
                        model=model,
                        parameter_point_id=f"thermal_photon_{pidx:03d}",
                        probe_id=probe_id,
                        rho=rho,
                        time=time,
                        parameters=parameters,
                        channel=channel,
                        choi=choi,
                        after=apply_kraus(rho, kraus),
                        representation_origin="thermal_lindblad_semigroup",
                        physical_regime="finite_temperature_photon_exchange",
                        extra={
                            "thermal_mean_occupation": float(nbar),
                            "equilibrium_excited_population": float(
                                equilibrium_excited
                            ),
                            "transition_frequency_hz": float(
                                config.thermal_photon_transition_frequency_hz
                            ),
                        },
                    )
                )

    # 6) Quantized mechanical/acoustic excitation-exchange mode.
    model = registry.get("mechanical-phonon-mode")
    for pidx, (frequency_hz, coupling_hz, temperature) in enumerate(
        product(
            config.mechanical_frequencies_hz,
            config.mechanical_couplings_hz,
            config.mechanical_temperatures_k,
        )
    ):
        omega = 2.0 * np.pi * frequency_hz
        coupling = 2.0 * np.pi * coupling_hz
        nbar = thermal_mean_occupation(omega, temperature)
        for time in config.mechanical_times_s:
            parameters = {
                "mode_angular_frequency": float(omega),
                "coupling_rate": float(coupling),
                "temperature_kelvin": float(temperature),
                "interaction_time": float(time),
            }
            kraus = mechanical_phonon_kraus(
                mode_angular_frequency=omega,
                coupling_rate=coupling,
                temperature_kelvin=temperature,
                mode_dimension=config.mechanical_mode_dimension,
                time=time,
            )
            channel, choi = describe_kraus_channel(kraus)
            for probe_id, rho in probes.items():
                samples.append(
                    _sample(
                        model=model,
                        parameter_point_id=f"mechanical_{pidx:03d}",
                        probe_id=probe_id,
                        rho=rho,
                        time=time,
                        parameters=parameters,
                        channel=channel,
                        choi=choi,
                        after=apply_kraus(rho, kraus),
                        representation_origin="thermal_mechanical_mode_partial_trace",
                        physical_regime="qubit_phonon_exchange",
                        extra={
                            "thermal_mean_occupation": nbar,
                            "mode_frequency_hz": float(frequency_hz),
                            "coupling_hz": float(coupling_hz),
                        },
                        numerical_metadata={
                            "mechanical_mode_dimension": config.mechanical_mode_dimension
                        },
                    )
                )


    # 7) Single-mode mechanical/phonon longitudinal pure dephasing.
    model = registry.get("single-mode-mechanical-phonon-dephasing")
    for pidx, (frequency_hz, coupling_hz, occupation) in enumerate(
        product(
            config.mechanical_longitudinal_frequencies_hz,
            config.mechanical_longitudinal_couplings_hz,
            config.mechanical_longitudinal_occupations,
        )
    ):
        omega = 2.0 * np.pi * frequency_hz
        coupling = 2.0 * np.pi * coupling_hz
        for time in config.mechanical_longitudinal_times_s:
            parameters = {
                "mode_angular_frequency": float(omega),
                "coupling_rate": float(coupling),
                "thermal_occupation": float(occupation),
                "interaction_time": float(time),
            }
            q = mechanical_coherence_factor(
                time=time,
                mode_angular_frequency=omega,
                coupling_rate=coupling,
                thermal_occupation=occupation,
            )
            exponent = mechanical_dephasing_exponent(
                time=time,
                mode_angular_frequency=omega,
                coupling_rate=coupling,
                thermal_occupation=occupation,
            )
            kraus = spin_boson_dephasing_kraus(q)
            channel, choi = describe_kraus_channel(kraus)
            for probe_id, rho in probes.items():
                samples.append(
                    _sample(
                        model=model,
                        parameter_point_id=f"mechanical_longitudinal_{pidx:03d}",
                        probe_id=probe_id,
                        rho=rho,
                        time=time,
                        parameters=parameters,
                        channel=channel,
                        choi=choi,
                        after=apply_kraus(rho, kraus),
                        representation_origin="exact_single_mode_longitudinal_bosonic_map",
                        physical_regime="mechanical_longitudinal_dephasing",
                        extra={
                            "coherence_factor": float(q),
                            "dephasing_exponent": float(exponent),
                            "mode_frequency_hz": float(frequency_hz),
                            "coupling_hz": float(coupling_hz),
                        },
                    )
                )

    # 8) Event-conditioned ionizing-radiation/quasiparticle burst.
    model = registry.get("ionizing-radiation-quasiparticle-burst")
    c_qp = 1.2 * (2.0 * np.pi * config.radiation_qubit_frequency_hz)
    for pidx, (x0, trapping) in enumerate(
        product(config.radiation_initial_xqp, config.radiation_trapping_rates_s)
    ):
        for time in config.radiation_times_s:
            parameters = {
                "initial_quasiparticle_fraction": float(x0),
                "recombination_rate": float(config.radiation_recombination_rate_s),
                "trapping_rate": float(trapping),
                "generation_rate": float(config.radiation_generation_rate_s),
                "qp_relaxation_coefficient": float(c_qp),
                "background_relaxation_rate": float(
                    config.radiation_background_relaxation_rate_s
                ),
                "interaction_time": float(time),
            }
            dynamic = {
                key: value
                for key, value in parameters.items()
                if key != "interaction_time"
            }
            x_qp, hazard = quasiparticle_fraction_and_hazard(
                time=time, **dynamic
            )
            kraus = ionizing_radiation_kraus(time=time, **dynamic)
            probability = 1.0 - np.exp(-hazard)
            channel, choi = describe_kraus_channel(kraus)
            for probe_id, rho in probes.items():
                samples.append(
                    _sample(
                        model=model,
                        parameter_point_id=f"radiation_{pidx:03d}",
                        probe_id=probe_id,
                        rho=rho,
                        time=time,
                        parameters=parameters,
                        channel=channel,
                        choi=choi,
                        after=apply_kraus(rho, kraus),
                        representation_origin="post_impact_quasiparticle_kinetics",
                        physical_regime="event_conditioned_ionizing_radiation",
                        extra={
                            "quasiparticle_fraction": x_qp,
                            "integrated_relaxation_hazard": hazard,
                            "effective_relaxation_probability": probability,
                        },
                    )
                )

    # 9) Bistable charge/TLS random-telegraph source.
    model = registry.get("bistable-charge-fluctuator-rtn")
    for pidx, (coupling_hz, switching_rate) in enumerate(
        product(config.charge_couplings_hz, config.charge_switching_rates_s)
    ):
        coupling = 2.0 * np.pi * coupling_hz
        corner_psd = random_telegraph_spectral_density(
            2.0 * switching_rate,
            coupling_rate=coupling,
            switching_rate=switching_rate,
        )
        for time in config.charge_times_s:
            parameters = {
                "coupling_rate": float(coupling),
                "switching_rate": float(switching_rate),
                "interaction_time": float(time),
            }
            w = random_telegraph_coherence_factor(
                coupling_rate=coupling,
                switching_rate=switching_rate,
                time=time,
            )
            kraus = random_telegraph_dephasing_kraus(
                coupling_rate=coupling,
                switching_rate=switching_rate,
                time=time,
            )
            channel, choi = describe_kraus_channel(kraus)
            for probe_id, rho in probes.items():
                samples.append(
                    _sample(
                        model=model,
                        parameter_point_id=f"charge_rtn_{pidx:03d}",
                        probe_id=probe_id,
                        rho=rho,
                        time=time,
                        parameters=parameters,
                        channel=channel,
                        choi=choi,
                        after=apply_kraus(rho, kraus),
                        representation_origin="exact_random_telegraph_ensemble",
                        physical_regime="bistable_charge_fluctuation",
                        extra={
                            "coherence_factor": w,
                            "rtn_psd_at_2nu": corner_psd,
                            "coupling_hz": float(coupling_hz),
                        },
                    )
                )

    if len(samples) != config.expected_sample_count:
        raise RuntimeError(
            f"Generated {len(samples)} samples; expected {config.expected_sample_count}."
        )
    return samples
