import numpy as np
from scipy.linalg import expm

from ic_quantum.core.probes import standard_probe_densities
from ic_quantum.core.validation import validate_density_matrix, validate_kraus, validate_unitary
from ic_quantum.dynamics.charge_fluctuator import (
    random_telegraph_coherence_factor,
    random_telegraph_dephasing_kraus,
)
from ic_quantum.dynamics.external_field import (
    external_magnetic_field_unitary,
    integrated_zeeman_angle,
)
from ic_quantum.dynamics.mechanical_phonon import (
    mechanical_joint_angular_hamiltonian,
    mechanical_joint_unitary,
    mechanical_phonon_kraus,
    reduced_mechanical_phonon_dynamics,
)
from ic_quantum.dynamics.open_system import apply_kraus
from ic_quantum.dynamics.radiation import (
    ionizing_radiation_relaxation_probability,
    quasiparticle_fraction_and_hazard,
)


def test_external_field_zero_amplitude_is_identity():
    u = external_magnetic_field_unitary(
        gyromagnetic_ratio=1.0,
        field_amplitude=0.0,
        drive_angular_frequency=2.0,
        phase=0.3,
        polar_angle=np.pi / 2,
        azimuth_angle=0.0,
        time=3.0,
    )
    assert np.allclose(u, np.eye(2), atol=1e-12)
    validate_unitary(u)


def test_external_dc_z_field_matches_expected_rotation():
    angle = integrated_zeeman_angle(
        gyromagnetic_ratio=1.0,
        field_amplitude=1.0,
        drive_angular_frequency=0.0,
        phase=0.0,
        time=np.pi,
    )
    assert np.isclose(angle, np.pi)
    u = external_magnetic_field_unitary(
        gyromagnetic_ratio=1.0,
        field_amplitude=1.0,
        drive_angular_frequency=0.0,
        phase=0.0,
        polar_angle=0.0,
        azimuth_angle=0.0,
        time=np.pi,
    )
    expected = np.diag([-1.0j, 1.0j])
    assert np.allclose(u, expected, atol=1e-10)


def test_mechanical_joint_hamiltonian_and_unitary_are_physical():
    h = mechanical_joint_angular_hamiltonian(
        mode_angular_frequency=3.0,
        coupling_rate=0.4,
        mode_dimension=3,
    )
    assert np.allclose(h, h.conjugate().T, atol=1e-12)
    u = mechanical_joint_unitary(
        time=0.8,
        mode_angular_frequency=3.0,
        coupling_rate=0.4,
        mode_dimension=3,
    )
    validate_unitary(u)


def test_mechanical_kraus_matches_explicit_partial_trace():
    rho = standard_probe_densities()["+i"]
    kwargs = dict(
        mode_angular_frequency=2.0 * np.pi * 1.0e6,
        coupling_rate=2.0 * np.pi * 0.1e6,
        temperature_kelvin=0.02,
        mode_dimension=5,
        time=0.7e-6,
    )
    reduced = reduced_mechanical_phonon_dynamics(rho, **kwargs)
    kraus = mechanical_phonon_kraus(**kwargs)
    via_kraus = apply_kraus(rho, kraus)
    validate_kraus(kraus)
    validate_density_matrix(reduced)
    assert np.allclose(reduced, via_kraus, atol=1e-9, rtol=0.0)


def test_mechanical_zero_coupling_leaves_qubit_state_invariant():
    rho = standard_probe_densities()["+"]
    after = reduced_mechanical_phonon_dynamics(
        rho,
        mode_angular_frequency=2.0 * np.pi * 1.0e6,
        coupling_rate=0.0,
        temperature_kelvin=0.05,
        mode_dimension=4,
        time=2.0e-6,
    )
    # Free qubit evolution is retained by the full model, so a phase-sensitive
    # input changes. Computational populations are the correct zero-coupling invariant.
    assert np.allclose(np.diag(after), np.diag(rho), atol=1e-10)


def test_radiation_trapping_only_matches_analytic_hazard():
    x0 = 2.0e-5
    s = 1000.0
    c = 2.0e10
    t = 2.0e-3
    x, hazard = quasiparticle_fraction_and_hazard(
        initial_quasiparticle_fraction=x0,
        recombination_rate=0.0,
        trapping_rate=s,
        generation_rate=0.0,
        qp_relaxation_coefficient=c,
        background_relaxation_rate=0.0,
        time=t,
    )
    expected_x = x0 * np.exp(-s * t)
    expected_h = c * x0 * (1.0 - np.exp(-s * t)) / s
    assert np.isclose(x, expected_x, rtol=1e-7)
    assert np.isclose(hazard, expected_h, rtol=1e-7)
    p = ionizing_radiation_relaxation_probability(
        initial_quasiparticle_fraction=x0,
        recombination_rate=0.0,
        trapping_rate=s,
        generation_rate=0.0,
        qp_relaxation_coefficient=c,
        background_relaxation_rate=0.0,
        time=t,
    )
    assert np.isclose(p, 1.0 - np.exp(-expected_h), rtol=1e-7)


def test_random_telegraph_exact_factor_matches_conditional_generator():
    v = 3.0
    nu = 1.2
    t = 0.7
    generator = np.array(
        [[-nu - 1.0j * v, nu], [nu, -nu + 1.0j * v]],
        dtype=complex,
    )
    conditional = expm(generator * t) @ np.array([0.5, 0.5], dtype=complex)
    expected = float(np.real(np.sum(conditional)))
    actual = random_telegraph_coherence_factor(
        coupling_rate=v,
        switching_rate=nu,
        time=t,
    )
    assert np.isclose(actual, expected, atol=1e-10)
    validate_kraus(
        random_telegraph_dephasing_kraus(
            coupling_rate=v,
            switching_rate=nu,
            time=t,
        )
    )
