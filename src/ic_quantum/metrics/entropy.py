"""Von Neumann entropy."""

from __future__ import annotations

import numpy as np

from ic_quantum.core.validation import validate_density_matrix


def von_neumann_entropy(rho: np.ndarray, base: float = 2.0) -> float:
    """S(rho) = -Tr[rho log_base(rho)], evaluated from rho eigenvalues."""
    validate_density_matrix(rho)
    if base <= 0 or np.isclose(base, 1.0):
        raise ValueError("Logarithm base must be positive and different from 1.")
    eigenvalues = np.linalg.eigvalsh(rho).real
    eigenvalues = np.clip(eigenvalues, 0.0, 1.0)
    nonzero = eigenvalues[eigenvalues > 1e-15]
    if nonzero.size == 0:
        return 0.0
    return float(-np.sum(nonzero * (np.log(nonzero) / np.log(base))))
