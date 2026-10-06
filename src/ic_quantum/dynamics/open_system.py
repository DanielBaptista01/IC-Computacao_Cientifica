"""Reduced open-system dynamics through explicit Kraus sums."""

from __future__ import annotations

import numpy as np

from ic_quantum.core.validation import validate_density_matrix, validate_kraus


def apply_kraus(rho: np.ndarray, kraus_ops: list[np.ndarray]) -> np.ndarray:
    """Apply E(rho) = sum_i K_i rho K_i^dagger for a trace-preserving channel."""
    validate_density_matrix(rho)
    validate_kraus(kraus_ops)
    output = np.zeros_like(rho, dtype=complex)
    for operator in kraus_ops:
        output += operator @ rho @ operator.conjugate().T
    output = 0.5 * (output + output.conjugate().T)
    validate_density_matrix(output)
    return output
