"""Quantum-state purity."""

from __future__ import annotations

import numpy as np

from ic_quantum.core.validation import validate_density_matrix


def purity(rho: np.ndarray) -> float:
    """P(rho) = Tr(rho^2)."""
    validate_density_matrix(rho)
    return float(np.real(np.trace(rho @ rho)))
