"""Generation of the physical-source causal-agent expansion v2."""

from __future__ import annotations
from itertools import product
import numpy as np

from ic_quantum.core.probes import final_probe_densities
from ic_quantum.data.causal_agent_schema import CausalAgentSampleRecord
from ic_quantum.data.channel_descriptors import describe_kraus_channel, describe_unitary_channel
from ic_quantum.data.final_generator import generate_final_dataset_samples
from ic_quantum.data.generator import build_signature
from ic_quantum.data.physical_catalog_v2 import build_physical_v2_registry
from ic_quantum.data.physical_protocol_v2 import PhysicalV2Config
from ic_quantum.data.validator import validate_sample_record
from ic_quantum.dynamics.electromagnetic_drive import em_drive_unitary
from ic_quantum.dynamics.magnetic_field import magnetic_field_unitary
from ic_quantum.dynamics.mechanical_mode import (
    apply_mechanical_mode_dephasing, mechanical_coherence_factor,
)
from ic_quantum.dynamics.thermal_reservoir import (
    apply_thermal_photon_reservoir, bose_occupation,
    generalized_amplitude_damping_kraus,
)
from ic_quantum.dynamics.closed_system import apply_unitary
from ic_quantum.dynamics.spin_boson import spin_boson_dephasing_kraus


def _decorate_baseline_samples(samples, registry):
    for sample in samples:
        model=registry.get(sample.agent_model_id)
        sample.metadata["physical_source"]=model.physical_category
        sample.metadata["causal_mechanism"]=model.coupling_mechanism
        sample.metadata["dataset_component"]="mechanistic_baseline_resampled_for_v2"
        sample.signature.physical_parameters=dict(sample.parameter_values)
    return samples


def _make_sample(*, model, sample_id, parameter_values, time, probe_id, rho_before,
                 rho_after, channel_desc, choi_desc, parameter_point_id,
                 representation_origin, physical_parameters, spectral_descriptors):
    signature=build_signature(
        rho_before,rho_after,time=time,
        channel_descriptors=channel_desc,choi_descriptors=choi_desc,
    )
    signature.physical_parameters=dict(physical_parameters)
    signature.extra["spectral_descriptors"]=spectral_descriptors
    sample=CausalAgentSampleRecord(
        sample_id=sample_id,
        agent_model_id=model.agent_id,
        parameter_values=parameter_values,
        time=float(time),
        initial_system_state=probe_id,
        signature=signature,
        random_seed=None,
        metadata={
            "deterministic":True,
            "parameter_point_id":parameter_point_id,
            "representation_origin":representation_origin,
            "physical_source":model.physical_category,
            "causal_mechanism":model.coupling_mechanism,
            "dataset_component":"physical_source_expansion_v2",
        },
    )
    validate_sample_record(sample,model)
    return sample


def _orientation_vector(name: str, amplitude: float) -> tuple[float,float,float]:
    if name=="x": return (amplitude,0.0,0.0)
    if name=="z": return (0.0,0.0,amplitude)
    if name=="xz":
        v=amplitude/np.sqrt(2.0)
        return (v,0.0,v)
    raise ValueError(f"Unknown magnetic orientation: {name}")


def generate_physical_v2_samples(config: PhysicalV2Config) -> list[CausalAgentSampleRecord]:
    registry=build_physical_v2_registry()
    probes={k:final_probe_densities()[k] for k in config.probe_ids}
    samples=_decorate_baseline_samples(
        generate_final_dataset_samples(config.base_config),registry
    )

    em_model=registry.get("external-electromagnetic-rabi-drive")
    for p_index,(rabi,detuning,phase) in enumerate(product(config.em_rabi_rates,config.em_detunings,config.em_phases)):
        pid=f"em_{p_index:02d}"
        for t in config.time_values_s:
            u=em_drive_unitary(rabi,detuning,phase,t)
            cdesc,chdesc=describe_unitary_channel(u)
            for probe_id,rho in probes.items():
                after=apply_unitary(rho,u)
                samples.append(_make_sample(
                    model=em_model,
                    sample_id=f"{em_model.agent_id}__{pid}__{probe_id}__t{t:.12g}",
                    parameter_values={"rabi_rate":float(rabi),"detuning":float(detuning),"phase":float(phase),"interaction_time":float(t)},
                    time=t,probe_id=probe_id,rho_before=rho,rho_after=after,
                    channel_desc=cdesc,choi_desc=chdesc,parameter_point_id=pid,
                    representation_origin="semiclassical_em_rwa_hamiltonian",
                    physical_parameters={"effective_rabi_rate_rad_s":float(rabi),"detuning_rad_s":float(detuning),"phase_rad":float(phase)},
                    spectral_descriptors={"source_type":"monochromatic_coherent_drive","detuning_rad_s":float(detuning)},
                ))

    mag_model=registry.get("external-magnetic-zeeman-field")
    for p_index,(amplitude,orientation) in enumerate(product(config.magnetic_field_amplitudes_t,config.magnetic_orientations)):
        pid=f"mag_{p_index:02d}"
        field=_orientation_vector(orientation,float(amplitude))
        for t in config.time_values_s:
            u=magnetic_field_unitary(field,config.gyromagnetic_ratio_rad_s_t,t)
            cdesc,chdesc=describe_unitary_channel(u)
            for probe_id,rho in probes.items():
                after=apply_unitary(rho,u)
                samples.append(_make_sample(
                    model=mag_model,
                    sample_id=f"{mag_model.agent_id}__{pid}__{probe_id}__t{t:.12g}",
                    parameter_values={"field_x":field[0],"field_y":field[1],"field_z":field[2],"gyromagnetic_ratio":config.gyromagnetic_ratio_rad_s_t,"interaction_time":float(t)},
                    time=t,probe_id=probe_id,rho_before=rho,rho_after=after,
                    channel_desc=cdesc,choi_desc=chdesc,parameter_point_id=pid,
                    representation_origin="zeeman_hamiltonian",
                    physical_parameters={"field_amplitude_tesla":float(amplitude),"orientation":orientation,"gyromagnetic_ratio_rad_s_t":float(config.gyromagnetic_ratio_rad_s_t)},
                    spectral_descriptors={"source_type":"quasistatic_field","dominant_frequency_hz":0.0},
                ))

    thermal_model=registry.get("thermal-photon-reservoir")
    for p_index,(gamma,temp) in enumerate(product(config.thermal_decay_rates,config.thermal_temperatures_k)):
        pid=f"thermal_{p_index:02d}"
        nbar=bose_occupation(config.thermal_transition_angular_frequency,temp)
        for t in config.time_values_s:
            kraus=generalized_amplitude_damping_kraus(gamma,nbar,t)
            cdesc,chdesc=describe_kraus_channel(kraus)
            for probe_id,rho in probes.items():
                after=apply_thermal_photon_reservoir(
                    rho,decay_rate=gamma,
                    transition_angular_frequency=config.thermal_transition_angular_frequency,
                    temperature_kelvin=temp,time=t,
                )
                samples.append(_make_sample(
                    model=thermal_model,
                    sample_id=f"{thermal_model.agent_id}__{pid}__{probe_id}__t{t:.12g}",
                    parameter_values={"decay_rate":float(gamma),"transition_angular_frequency":float(config.thermal_transition_angular_frequency),"temperature_kelvin":float(temp),"interaction_time":float(t)},
                    time=t,probe_id=probe_id,rho_before=rho,rho_after=after,
                    channel_desc=cdesc,choi_desc=chdesc,parameter_point_id=pid,
                    representation_origin="thermal_markovian_master_equation",
                    physical_parameters={"temperature_kelvin":float(temp),"thermal_occupation":float(nbar),"downward_rate_s":float(gamma*(nbar+1.0)),"upward_rate_s":float(gamma*nbar)},
                    spectral_descriptors={"source_type":"thermal_photon_reservoir","transition_angular_frequency_rad_s":float(config.thermal_transition_angular_frequency),"bose_occupation":float(nbar)},
                ))

    mech_model=registry.get("single-mode-mechanical-phonon-dephasing")
    for p_index,(omega,g,nbar) in enumerate(product(config.mechanical_mode_frequencies,config.mechanical_couplings,config.mechanical_occupations)):
        pid=f"mech_{p_index:02d}"
        for t in config.time_values_s:
            q=mechanical_coherence_factor(t,omega,g,nbar)
            kraus=spin_boson_dephasing_kraus(q)
            cdesc,chdesc=describe_kraus_channel(kraus)
            cdesc["coherence_factor"]=q
            for probe_id,rho in probes.items():
                after=apply_mechanical_mode_dephasing(
                    rho,time=t,mode_angular_frequency=omega,
                    coupling_rate=g,thermal_occupation=nbar,
                )
                samples.append(_make_sample(
                    model=mech_model,
                    sample_id=f"{mech_model.agent_id}__{pid}__{probe_id}__t{t:.12g}",
                    parameter_values={"mode_angular_frequency":float(omega),"coupling_rate":float(g),"thermal_occupation":float(nbar),"interaction_time":float(t)},
                    time=t,probe_id=probe_id,rho_before=rho,rho_after=after,
                    channel_desc=cdesc,choi_desc=chdesc,parameter_point_id=pid,
                    representation_origin="single_mode_bosonic_dephasing",
                    physical_parameters={"mode_angular_frequency_rad_s":float(omega),"mode_frequency_hz":float(omega/(2*np.pi)),"coupling_rate_rad_s":float(g),"thermal_occupation":float(nbar)},
                    spectral_descriptors={"source_type":"single_mechanical_spectral_line","mode_angular_frequency_rad_s":float(omega),"line_weight_proxy":float(g*g)},
                ))

    if len(samples)!=config.expected_sample_count:
        raise RuntimeError(f"Generated {len(samples)} samples; expected {config.expected_sample_count}.")
    return samples
