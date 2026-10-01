"""Explicit finite system-agent interaction models."""

from __future__ import annotations

import numpy as np

from ic_quantum.core.states import reference_density
from ic_quantum.dynamics.closed_system import apply_unitary, unitary_from_hamiltonian
from ic_quantum.dynamics.partial_trace import partial_trace_bipartite


def exchange_interaction_hamiltonian(coupling: float, hbar: float = 1.0) -> np.ndarray:
    """H_int = i*hbar*g(|01><10| - |10><01|)."""
    if hbar <= 0:
        raise ValueError("hbar must be positive.")
    g = float(coupling)
    h = np.zeros((4, 4), dtype=complex)
    h[1, 2] = 1.0j * hbar * g
    h[2, 1] = -1.0j * hbar * g
    return h


def exchange_unitary(coupling: float, time: float, hbar: float = 1.0) -> np.ndarray:
    return unitary_from_hamiltonian(
        exchange_interaction_hamiltonian(coupling, hbar=hbar),
        time=time,
        hbar=hbar,
    )


def exchange_amplitude_damping_probability(coupling: float, time: float) -> float:
    return float(np.sin(float(coupling) * float(time)) ** 2)


def reduced_exchange_dynamics(
    rho_system: np.ndarray,
    coupling: float,
    time: float,
    hbar: float = 1.0,
) -> np.ndarray:
    """Evolve S+A with A in |0>, then trace A."""
    rho_agent = reference_density("0")
    rho_joint = np.kron(rho_system, rho_agent)
    evolved = apply_unitary(
        rho_joint,
        exchange_unitary(coupling=coupling, time=time, hbar=hbar),
    )
    return partial_trace_bipartite(evolved, dims=(2, 2), trace_out="B")
