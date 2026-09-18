"""Closed-system evolution implemented directly from matrix algebra."""

from __future__ import annotations

import numpy as np
from scipy.linalg import expm

from ic_quantum.core.validation import validate_density_matrix, validate_unitary


def unitary_from_hamiltonian(
    hamiltonian: np.ndarray,
    time: float,
    hbar: float = 1.0,
) -> np.ndarray:
    """Compute U(t) = exp(-i H t / hbar) for a time-independent Hamiltonian."""
    hamiltonian = np.asarray(hamiltonian, dtype=complex)
    if hamiltonian.ndim != 2 or hamiltonian.shape[0] != hamiltonian.shape[1]:
        raise ValueError("Hamiltonian must be a square matrix.")
    if not np.allclose(hamiltonian, hamiltonian.conjugate().T, atol=1e-10, rtol=0.0):
        raise ValueError("Hamiltonian must be Hermitian.")
    if hbar <= 0:
        raise ValueError("hbar must be positive.")
    unitary = expm(-1.0j * hamiltonian * time / hbar)
    validate_unitary(unitary)
    return unitary


def apply_unitary(rho: np.ndarray, unitary: np.ndarray) -> np.ndarray:
    """Apply rho' = U rho U^dagger."""
    validate_density_matrix(rho)
    validate_unitary(unitary)
    output = unitary @ rho @ unitary.conjugate().T
    output = 0.5 * (output + output.conjugate().T)
    validate_density_matrix(output)
    return output
