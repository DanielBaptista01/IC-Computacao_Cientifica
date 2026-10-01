"""State-space distances used in identifiability analysis."""

from __future__ import annotations

import numpy as np

from ic_quantum.core.validation import validate_density_matrix


def trace_distance(rho: np.ndarray, sigma: np.ndarray) -> float:
    """Return D(rho,sigma)=1/2 ||rho-sigma||_1.

    For density matrices the difference is Hermitian, so the trace norm is the
    sum of the absolute eigenvalues. The value lies in [0, 1].
    """
    rho = np.asarray(rho, dtype=complex)
    sigma = np.asarray(sigma, dtype=complex)
    validate_density_matrix(rho)
    validate_density_matrix(sigma)
    if rho.shape != sigma.shape:
        raise ValueError("rho and sigma must have the same Hilbert-space dimension.")
    delta = 0.5 * ((rho - sigma) + (rho - sigma).conjugate().T)
    value = 0.5 * float(np.sum(np.abs(np.linalg.eigvalsh(delta))))
    return float(np.clip(value, 0.0, 1.0))
