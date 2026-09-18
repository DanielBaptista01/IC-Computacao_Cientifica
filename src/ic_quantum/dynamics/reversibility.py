"""Reversibility diagnostics for finite-dimensional quantum channels.

The module separates:
1. linear invertibility of the superoperator;
2. existence of a CPTP inverse;
3. direct reversibility by a unitary acting on the observed system.

Conditional recovery, environment-assisted recovery and approximate mitigation are
not inferred from the reduced channel alone and remain model-dependent questions.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ic_quantum.core.validation import (\n    DEFAULT_ATOL,\n    validate_density_matrix,\n    validate_kraus,\n    validate_unitary,\n)


@dataclass(frozen=True, slots=True)
class ReversibilityAssessment:
    """Numerical diagnostics for the reduced quantum map."""

    is_cptp: bool
    linear_invertible: bool
    inverse_cptp: bool | None
    direct_unitary_inverse: bool
    choi_rank: int
    condition_number: float | None
    classification: str


def superoperator_from_kraus(kraus_ops: list[np.ndarray]) -> np.ndarray:
    """Return the Liouville superoperator for column-stacked density matrices.

    With vec(X) using column-major order,
    vec(K X K^dagger) = (K* tensor K) vec(X).
    """
    validate_kraus(kraus_ops)
    dimension = np.asarray(kraus_ops[0], dtype=complex).shape[0]
    superoperator = np.zeros((dimension**2, dimension**2), dtype=complex)
    for operator in kraus_ops:
        operator = np.asarray(operator, dtype=complex)
        superoperator += np.kron(operator.conjugate(), operator)
    return superoperator


def superoperator_from_unitary(unitary: np.ndarray) -> np.ndarray:
    """Return the superoperator of rho -> U rho U^dagger."""
    validate_unitary(unitary)
    return np.kron(unitary.conjugate(), unitary)


def _validate_superoperator(superoperator: np.ndarray, dimension: int) -> np.ndarray:
    superoperator = np.asarray(superoperator, dtype=complex)
    expected = dimension**2
    if dimension <= 0 or superoperator.shape != (expected, expected):
        raise ValueError("Superoperator shape is incompatible with the Hilbert-space dimension.")
    return superoperator


def choi_from_superoperator(superoperator: np.ndarray, dimension: int) -> np.ndarray:
    """Construct J(E) = sum_ij |i><j| tensor E(|i><j|)."""
    superoperator = _validate_superoperator(superoperator, dimension)
    choi = np.zeros((dimension**2, dimension**2), dtype=complex)
    for i in range(dimension):
        for j in range(dimension):
            basis = np.zeros((dimension, dimension), dtype=complex)
            basis[i, j] = 1.0
            output = (
                superoperator @ basis.reshape(-1, order="F")
            ).reshape((dimension, dimension), order="F")
            choi[
                i * dimension : (i + 1) * dimension,
                j * dimension : (j + 1) * dimension,
            ] = output
    return choi


def is_completely_positive_superoperator(
    superoperator: np.ndarray,
    dimension: int,
    atol: float = DEFAULT_ATOL,
) -> bool:
    """Check complete positivity through Choi's criterion."""
    choi = choi_from_superoperator(superoperator, dimension)
    if not np.allclose(choi, choi.conjugate().T, atol=atol, rtol=0.0):
        return False
    eigenvalues = np.linalg.eigvalsh(0.5 * (choi + choi.conjugate().T))
    return bool(np.min(eigenvalues) >= -atol)


def is_trace_preserving_superoperator(
    superoperator: np.ndarray,
    dimension: int,
    atol: float = DEFAULT_ATOL,
) -> bool:
    """Check Tr[E(X)] = Tr[X] using the partial trace of the Choi matrix."""
    choi = choi_from_superoperator(superoperator, dimension)
    traced_output = np.zeros((dimension, dimension), dtype=complex)
    for i in range(dimension):
        for j in range(dimension):
            block = choi[
                i * dimension : (i + 1) * dimension,
                j * dimension : (j + 1) * dimension,
            ]
            traced_output[i, j] = np.trace(block)
    return np.allclose(
        traced_output,
        np.eye(dimension, dtype=complex),
        atol=atol,
        rtol=0.0,
    )


def is_cptp_superoperator(
    superoperator: np.ndarray,
    dimension: int,
    atol: float = DEFAULT_ATOL,
) -> bool:
    """Return True when the map is both completely positive and trace preserving."""
    return is_completely_positive_superoperator(
        superoperator, dimension, atol
    ) and is_trace_preserving_superoperator(superoperator, dimension, atol)


def assess_superoperator_reversibility(
    superoperator: np.ndarray,
    dimension: int,
    atol: float = DEFAULT_ATOL,
) -> ReversibilityAssessment:
    """Assess reduced-map reversibility without conflating distinct notions.

    A linearly invertible reduced channel may still have a non-CP inverse. For
    equal input/output dimensions, a CPTP channel with a CPTP inverse is a
    unitary channel, so direct unitary reversibility is identified by the
    rank-one Choi representation.
    """
    superoperator = _validate_superoperator(superoperator, dimension)
    is_cptp = is_cptp_superoperator(superoperator, dimension, atol)
    rank = int(np.linalg.matrix_rank(superoperator, tol=atol))
    linear_invertible = rank == dimension**2

    choi = choi_from_superoperator(superoperator, dimension)
    choi_hermitian = 0.5 * (choi + choi.conjugate().T)
    choi_rank = int(np.linalg.matrix_rank(choi_hermitian, tol=atol))
    direct_unitary_inverse = bool(is_cptp and choi_rank == 1)

    inverse_cptp: bool | None = None
    condition_number: float | None = None
    if linear_invertible:
        condition_number = float(np.linalg.cond(superoperator))
        inverse = np.linalg.inv(superoperator)
        inverse_cptp = is_cptp_superoperator(inverse, dimension, atol)

    if not is_cptp:
        classification = "invalid_or_non_cptp_map"
    elif direct_unitary_inverse:
        classification = "class_I_direct_unitary_reversible"
    elif not linear_invertible:
        classification = "class_II_reduced_nonunitary_noninvertible"
    elif inverse_cptp is False:
        classification = "class_II_linearly_invertible_without_CPTP_inverse"
    else:
        classification = "class_III_requires_structured_recovery_analysis"

    return ReversibilityAssessment(
        is_cptp=is_cptp,
        linear_invertible=linear_invertible,
        inverse_cptp=inverse_cptp,
        direct_unitary_inverse=direct_unitary_inverse,
        choi_rank=choi_rank,
        condition_number=condition_number,
        classification=classification,
    )


def assess_kraus_reversibility(
    kraus_ops: list[np.ndarray],
    atol: float = DEFAULT_ATOL,
) -> ReversibilityAssessment:
    """Assess a CPTP channel provided through a Kraus representation."""
    superoperator = superoperator_from_kraus(kraus_ops)
    dimension = np.asarray(kraus_ops[0]).shape[0]
    return assess_superoperator_reversibility(superoperator, dimension, atol)


def assess_unitary_reversibility(
    unitary: np.ndarray,
    atol: float = DEFAULT_ATOL,
) -> ReversibilityAssessment:
    """Assess a unitary channel used as the positive reversibility control."""
    unitary = np.asarray(unitary, dtype=complex)
    validate_unitary(unitary, atol=atol)
    return assess_superoperator_reversibility(
        superoperator_from_unitary(unitary),
        unitary.shape[0],
        atol,
    )


def max_unitary_recovery_fidelity_to_pure_target(
    rho_after: np.ndarray,
    target_rho: np.ndarray,
    atol: float = DEFAULT_ATOL,
) -> float:
    """Upper bound for recovery of a pure target using only a system unitary.

    For a pure target |psi><psi|, maximizing
    <psi| U rho_after U^dagger |psi> over all unitaries U yields the largest
    eigenvalue of rho_after. The reason is spectral: a unitary may rotate the
    eigenvectors but cannot change the eigenvalues (or purity) of rho_after.

    Therefore, if a channel maps a pure state to a genuinely mixed state,
    lambda_max(rho_after) < 1 proves that no single unitary acting only on the
    observed system can perfectly recover that target state.
    """
    rho_after = np.asarray(rho_after, dtype=complex)
    target_rho = np.asarray(target_rho, dtype=complex)
    validate_density_matrix(rho_after, atol=atol)
    validate_density_matrix(target_rho, atol=atol)

    target_purity = float(np.real(np.trace(target_rho @ target_rho)))
    if not np.isclose(target_purity, 1.0, atol=atol, rtol=0.0):
        raise ValueError("target_rho must be a pure-state density matrix.")

    eigenvalues = np.linalg.eigvalsh(0.5 * (rho_after + rho_after.conjugate().T))
    return float(np.clip(np.max(np.real(eigenvalues)), 0.0, 1.0))
