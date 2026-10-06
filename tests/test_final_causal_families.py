import numpy as np

from ic_quantum.channels.amplitude_damping import amplitude_damping_kraus
from ic_quantum.core.probes import standard_probe_densities
from ic_quantum.core.validation import validate_density_matrix, validate_kraus
from ic_quantum.data.final_catalog import build_final_registry
from ic_quantum.dynamics.markovian_reservoir import (
    apply_markovian_photon_reservoir_decay,
    markovian_decay_probability,
)
from ic_quantum.dynamics.open_system import apply_kraus
from ic_quantum.dynamics.spin_boson import (
    analytical_dephasing_map,
    apply_finite_mode_spin_boson_dephasing,
    finite_mode_coherence_factor,
    finite_mode_dephasing_exponent,
    spin_boson_dephasing_kraus,
)


def test_final_registry_contains_four_physical_model_families():
    registry = build_final_registry()
    assert registry.list_ids() == (
        "coherent-longitudinal-detuning",
        "finite-mode-spin-boson-dephasing",
        "finite-two-level-exchange-relaxation",
        "markovian-photon-reservoir-decay",
    )


def test_spin_boson_zero_time_is_identity_and_kraus_complete():
    probes = standard_probe_densities()
    q = finite_mode_coherence_factor(
        time=0.0,
        mode_count=4,
        cutoff_angular_frequency=2.0,
        temperature_angular_frequency=1.0,
    )
    assert np.isclose(q, 1.0)
    validate_kraus(spin_boson_dephasing_kraus(q))
    for rho in probes.values():
        after = apply_finite_mode_spin_boson_dephasing(
            rho,
            time=0.0,
            mode_count=4,
            cutoff_angular_frequency=2.0,
            temperature_angular_frequency=1.0,
        )
        assert np.allclose(after, rho, atol=1e-10, rtol=0.0)


def test_spin_boson_kraus_matches_exact_matrix_element_map():
    probes = standard_probe_densities()
    q = finite_mode_coherence_factor(
        time=0.73,
        mode_count=7,
        cutoff_angular_frequency=1.8,
        temperature_angular_frequency=0.9,
    )
    for rho in probes.values():
        via_kraus = apply_finite_mode_spin_boson_dephasing(
            rho,
            time=0.73,
            mode_count=7,
            cutoff_angular_frequency=1.8,
            temperature_angular_frequency=0.9,
        )
        direct = analytical_dephasing_map(rho, q)
        assert np.allclose(via_kraus, direct, atol=1e-10, rtol=0.0)
        validate_density_matrix(via_kraus)


def test_spin_boson_computational_populations_are_fixed():
    rho = standard_probe_densities()["+i"]
    after = apply_finite_mode_spin_boson_dephasing(
        rho,
        time=1.4,
        mode_count=16,
        cutoff_angular_frequency=2.0,
        temperature_angular_frequency=1.0,
    )
    assert np.allclose(np.diag(after), np.diag(rho), atol=1e-10, rtol=0.0)


def test_finite_spin_boson_has_exact_commensurate_revival():
    # Omega_k = k*Omega_c/N. At t=2*pi*N/Omega_c all cos(Omega_k t)=1.
    mode_count = 4
    cutoff = 2.0
    revival_time = 2.0 * np.pi * mode_count / cutoff
    exponent = finite_mode_dephasing_exponent(
        time=revival_time,
        mode_count=mode_count,
        cutoff_angular_frequency=cutoff,
        temperature_angular_frequency=1.0,
    )
    assert np.isclose(exponent, 0.0, atol=1e-10)
    assert np.isclose(
        finite_mode_coherence_factor(
            time=revival_time,
            mode_count=mode_count,
            cutoff_angular_frequency=cutoff,
            temperature_angular_frequency=1.0,
        ),
        1.0,
        atol=1e-10,
    )


def test_markovian_photon_decay_matches_exponential_population():
    rho_excited = standard_probe_densities()["1"]
    gamma = 0.7
    time = 1.3
    after = apply_markovian_photon_reservoir_decay(
        rho_excited, decay_rate=gamma, time=time
    )
    assert np.isclose(after[1, 1].real, np.exp(-gamma * time), atol=1e-10)
    assert np.isclose(after[0, 0].real, 1.0 - np.exp(-gamma * time), atol=1e-10)


def test_markovian_decay_boundaries_and_kraus_equivalence():
    rho = standard_probe_densities()["+i"]
    assert np.isclose(markovian_decay_probability(0.0, 5.0), 0.0)
    assert np.isclose(markovian_decay_probability(1.0, 0.0), 0.0)

    gamma = 0.4
    time = 2.2
    p = markovian_decay_probability(gamma, time)
    direct = apply_markovian_photon_reservoir_decay(
        rho, decay_rate=gamma, time=time
    )
    via_existing_channel = apply_kraus(rho, amplitude_damping_kraus(p))
    assert np.allclose(direct, via_existing_channel, atol=1e-10, rtol=0.0)


def test_distinct_exchange_and_markov_reservoir_can_share_same_reduced_channel():
    # This validates the causal-identifiability warning: distinct source models can
    # be exactly channel-equivalent for matched reduced damping probability.
    rho = standard_probe_densities()["+i"]
    p_target = 0.4
    gamma = 0.8
    time = -np.log(1.0 - p_target) / gamma
    reservoir = apply_markovian_photon_reservoir_decay(
        rho, decay_rate=gamma, time=time
    )
    canonical = apply_kraus(rho, amplitude_damping_kraus(p_target))
    assert np.allclose(reservoir, canonical, atol=1e-10, rtol=0.0)
