import numpy as np

from ic_quantum.channels.amplitude_damping import amplitude_damping_kraus
from ic_quantum.core.probes import standard_probe_densities
from ic_quantum.data.initial_catalog import build_initial_registry
from ic_quantum.dynamics.microscopic import (
    exchange_amplitude_damping_probability,
    exchange_interaction_hamiltonian,
    exchange_unitary,
    reduced_exchange_dynamics,
)
from ic_quantum.dynamics.open_system import apply_kraus


def test_initial_catalog_contains_models_not_channel_names():
    registry = build_initial_registry()
    assert registry.list_ids() == (
        "coherent-longitudinal-detuning",
        "finite-two-level-exchange-relaxation",
    )
    assert "dephasing" not in registry.list_ids()
    assert "amplitude_damping" not in registry.list_ids()


def test_exchange_hamiltonian_is_hermitian_and_unitary_evolution_is_valid():
    h = exchange_interaction_hamiltonian(coupling=0.4)
    assert np.allclose(h, h.conjugate().T, atol=1e-10, rtol=0.0)
    u = exchange_unitary(coupling=0.4, time=0.7)
    assert np.allclose(
        u.conjugate().T @ u,
        np.eye(4, dtype=complex),
        atol=1e-10,
        rtol=0.0,
    )


def test_exchange_reduced_dynamics_matches_amplitude_damping_on_all_probe_axes():
    coupling = 0.4
    time = 0.7
    p = exchange_amplitude_damping_probability(coupling, time)
    for rho in standard_probe_densities().values():
        microscopic = reduced_exchange_dynamics(rho, coupling=coupling, time=time)
        reduced_channel = apply_kraus(rho, amplitude_damping_kraus(p))
        assert np.allclose(microscopic, reduced_channel, atol=1e-10, rtol=0.0)


def test_exchange_endpoints_have_correct_reduced_limits():
    rho_excited = standard_probe_densities()["1"]
    no_interaction = reduced_exchange_dynamics(rho_excited, coupling=0.0, time=1.0)
    assert np.allclose(no_interaction, rho_excited, atol=1e-10, rtol=0.0)

    relaxed = reduced_exchange_dynamics(rho_excited, coupling=1.0, time=np.pi / 2.0)
    expected_ground = standard_probe_densities()["0"]
    assert np.allclose(relaxed, expected_ground, atol=1e-10, rtol=0.0)
