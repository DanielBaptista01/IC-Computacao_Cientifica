"""Partial trace for finite bipartite density matrices."""

from __future__ import annotations

import numpy as np

from ic_quantum.core.validation import validate_density_matrix


def partial_trace_bipartite(
    rho_ab: np.ndarray,
    dims: tuple[int, int],
    trace_out: str,
) -> np.ndarray:
    """Trace out subsystem 'A' or 'B' from rho_AB.

    The basis ordering is |a> tensor |b>, consistent with np.kron.
    """
    validate_density_matrix(rho_ab)
    dim_a, dim_b = dims
    if rho_ab.shape != (dim_a * dim_b, dim_a * dim_b):
        raise ValueError("rho_ab shape is incompatible with dims.")
    tensor = rho_ab.reshape(dim_a, dim_b, dim_a, dim_b)
    if trace_out.upper() == "A":
        reduced = np.trace(tensor, axis1=0, axis2=2)
    elif trace_out.upper() == "B":
        reduced = np.trace(tensor, axis1=1, axis2=3)
    else:
        raise ValueError("trace_out must be 'A' or 'B'.")
    reduced = 0.5 * (reduced + reduced.conjugate().T)
    validate_density_matrix(reduced)
    return reduced
