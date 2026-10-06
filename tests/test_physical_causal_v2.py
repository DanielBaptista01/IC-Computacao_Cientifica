import numpy as np

from ic_quantum.channels.amplitude_damping import amplitude_damping_kraus
from ic_quantum.core.probes import final_probe_densities
from ic_quantum.core.validation import validate_kraus
from ic_quantum.data.physical_catalog_v2 import build_physical_v2_registry
from ic_quantum.data.physical_protocol_v2 import PhysicalV2Config
from ic_quantum.data.physical_generator_v2 import generate_physical_v2_samples
from ic_quantum.data.physical_export_v2 import export_physical_v2
from ic_quantum.dynamics.electromagnetic_drive import em_drive_unitary
from ic_quantum.dynamics.magnetic_field import magnetic_field_unitary
from ic_quantum.dynamics.mechanical_mode import (
    mechanical_coherence_factor, apply_mechanical_mode_dephasing,
)
from ic_quantum.dynamics.thermal_reservoir import (
    bose_occupation, generalized_amplitude_damping_kraus,
    apply_thermal_photon_reservoir,
)
from ic_quantum.dynamics.closed_system import apply_unitary
from ic_quantum.dynamics.open_system import apply_kraus


def test_physical_v2_registry_contains_eight_validated_families():
    registry=build_physical_v2_registry()
    assert len(registry.list_ids()) == 8
    assert {
        "external-electromagnetic-rabi-drive",
        "external-magnetic-zeeman-field",
        "thermal-photon-reservoir",
        "single-mode-mechanical-phonon-dephasing",
    }.issubset(set(registry.list_ids()))


def test_resonant_em_pi_pulse_swaps_ground_to_excited():
    rho0=final_probe_densities()["0"]
    omega=2.0
    u=em_drive_unitary(omega,0.0,0.0,np.pi/omega)
    out=apply_unitary(rho0,u)
    assert np.allclose(out,final_probe_densities()["1"],atol=1e-10,rtol=0.0)


def test_magnetic_longitudinal_preserves_populations_and_transverse_pi_rotates():
    rho_plus=final_probe_densities()["+"]
    uz=magnetic_field_unitary((0.0,0.0,1.0),1.0,0.7)
    outz=apply_unitary(rho_plus,uz)
    assert np.allclose(np.diag(outz),np.diag(rho_plus),atol=1e-10,rtol=0.0)

    rho0=final_probe_densities()["0"]
    ux=magnetic_field_unitary((1.0,0.0,0.0),1.0,np.pi)
    outx=apply_unitary(rho0,ux)
    assert np.allclose(outx,final_probe_densities()["1"],atol=1e-10,rtol=0.0)


def test_thermal_reservoir_zero_temperature_reduces_to_amplitude_damping():
    rho=final_probe_densities()["+i"]
    gamma=0.7
    time=1.1
    nbar=bose_occupation(2*np.pi*5e9,0.0)
    assert nbar == 0.0
    thermal=apply_kraus(rho,generalized_amplitude_damping_kraus(gamma,nbar,time))
    canonical=apply_kraus(rho,amplitude_damping_kraus(1.0-np.exp(-gamma*time)))
    assert np.allclose(thermal,canonical,atol=1e-10,rtol=0.0)


def test_thermal_reservoir_relaxes_to_correct_finite_temperature_fixed_point():
    omega=2*np.pi*5e9
    temp=0.5
    gamma=2.0
    nbar=bose_occupation(omega,temp)
    rho1=final_probe_densities()["1"]
    out=apply_thermal_photon_reservoir(
        rho1,decay_rate=gamma,transition_angular_frequency=omega,
        temperature_kelvin=temp,time=50.0,
    )
    expected_excited=nbar/(2*nbar+1)
    assert np.isclose(out[1,1].real,expected_excited,atol=1e-10)


def test_mechanical_mode_has_exact_recurrence_and_preserves_populations():
    omega=2.0
    g=0.4
    nbar=1.5
    period=2*np.pi/omega
    assert np.isclose(mechanical_coherence_factor(period,omega,g,nbar),1.0,atol=1e-10)
    rho=final_probe_densities()["+i"]
    out=apply_mechanical_mode_dephasing(
        rho,time=0.73,mode_angular_frequency=omega,
        coupling_rate=g,thermal_occupation=nbar,
    )
    assert np.allclose(np.diag(out),np.diag(rho),atol=1e-10,rtol=0.0)


def test_thermal_and_mechanical_kraus_sets_are_cptp():
    validate_kraus(generalized_amplitude_damping_kraus(0.5,1.2,0.7))
    q=mechanical_coherence_factor(0.7,2.0,0.4,1.2)
    from ic_quantum.dynamics.spin_boson import spin_boson_dephasing_kraus
    validate_kraus(spin_boson_dephasing_kraus(q))


def _small_config():
    return PhysicalV2Config(
        time_min_s=0.0,time_max_s=1e-6,time_points=3,probe_ids=("0","+i"),
        coherent_detuning_rates=(1e6,),finite_exchange_couplings=(1e6,),
        photon_decay_rates=(5e5,),spin_boson_mode_counts=(4,),
        spin_boson_cutoffs=(1e6,),spin_boson_temperature_ratios=(1.0,),
        em_rabi_rates=(1e6,),em_detunings=(0.0,),em_phases=(0.0,),
        magnetic_field_amplitudes_t=(1e-6,),magnetic_orientations=("x",),
        thermal_decay_rates=(5e5,),thermal_temperatures_k=(0.1,),
        thermal_transition_angular_frequency=2*np.pi*5e9,
        mechanical_mode_frequencies=(2*np.pi*1e6,),
        mechanical_couplings=(2*np.pi*0.1e6,),mechanical_occupations=(1.0,),
    )


def test_physical_v2_small_dataset_has_all_eight_families_and_expected_count():
    config=_small_config()
    samples=generate_physical_v2_samples(config)
    assert config.expected_sample_count == 48
    assert len(samples) == 48
    assert len({s.agent_model_id for s in samples}) == 8
    assert len({s.sample_id for s in samples}) == 48


def test_physical_v2_export_keeps_source_labels_out_of_observable_features(tmp_path):
    config=_small_config()
    samples=generate_physical_v2_samples(config)
    paths=export_physical_v2(samples,config,tmp_path)
    feature_header=paths["observable_features_csv"].read_text(encoding="utf-8").splitlines()[0]
    label_header=paths["causal_labels_csv"].read_text(encoding="utf-8").splitlines()[0]
    assert "agent_model_id" not in feature_header
    assert "physical_source" not in feature_header
    assert "causal_mechanism" not in feature_header
    assert "physical_source" in label_header
    assert "causal_mechanism" in label_header
