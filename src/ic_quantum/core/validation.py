"""Numerical validation of quantum states, unitaries and Kraus representations."""

from __future__ import annotations

import numpy as np

DEFAULT_ATOL = 1e-10


def is_hermitian(matrix: np.ndarray, atol: float = DEFAULT_ATOL) -> bool:
    matrix = np.asarray(matrix, dtype=complex)
    return np.allclose(matrix, matrix.conjugate().T, atol=atol, rtol=0.0)


def has_unit_trace(rho: np.ndarray, atol: float = DEFAULT_ATOL) -> bool:
    return np.isclose(np.trace(rho), 1.0, atol=atol, rtol=0.0)


def is_positive_semidefinite(rho: np.ndarray, atol: float = DEFAULT_ATOL) -> bool:
    if not is_hermitian(rho, atol=atol):
        return False
    eigenvalues = np.linalg.eigvalsh(np.asarray(rho, dtype=complex))
    return bool(np.min(eigenvalues) >= -atol)


def validate_density_matrix(rho: np.ndarray, atol: float = DEFAULT_ATOL) -> None:
    rho = np.asarray(rho, dtype=complex)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        raise ValueError("Density matrix must be square.")
    if not is_hermitian(rho, atol=atol):
        raise ValueError("Density matrix is not Hermitian.")
    if not has_unit_trace(rho, atol=atol):
        raise ValueError(f"Density matrix trace must be 1; got {np.trace(rho)}.")
    if not is_positive_semidefinite(rho, atol=atol):
        raise ValueError("Density matrix is not positive semidefinite.")


def is_unitary(operator: np.ndarray, atol: float = DEFAULT_ATOL) -> bool:
    operator = np.asarray(operator, dtype=complex)
    if operator.ndim != 2 or operator.shape[0] != operator.shape[1]:
        return False
    identity = np.eye(operator.shape[0], dtype=complex)
    return np.allclose(operator.conjugate().T @ operator, identity, atol=atol, rtol=0.0)


def validate_unitary(operator: np.ndarray, atol: float = DEFAULT_ATOL) -> None:
    if not is_unitary(operator, atol=atol):
        raise ValueError("Operator is not unitary within the numerical tolerance.")


def kraus_completeness(kraus_ops: list[np.ndarray], atol: float = DEFAULT_ATOL) -> bool:
    if not kraus_ops:
        return False
    dimension = np.asarray(kraus_ops[0]).shape[0]
    accumulator = np.zeros((dimension, dimension), dtype=complex)
    for operator in kraus_ops:
        operator = np.asarray(operator, dtype=complex)
        if operator.shape != (dimension, dimension):
            return False
        accumulator += operator.conjugate().T @ operator
    return np.allclose(accumulator, np.eye(dimension), atol=atol, rtol=0.0)


def validate_kraus(kraus_ops: list[np.ndarray], atol: float = DEFAULT_ATOL) -> None:
    if not kraus_completeness(kraus_ops, atol=atol):
        raise ValueError("Kraus operators do not satisfy sum K_i^dagger K_i = I.")
