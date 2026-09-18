"""Latent causal transformations acting between programmed circuit depths.

A LatentCausalTransform is not a gate intentionally inserted by the programmer.
It is the explicit computational representation of the effective physical evolution
that occurs in the interval between programmed depths d and d+1.

The abstraction keeps the hypothesized physical cause (agent_id) separate from the
effective reduced transformation. Different physical agents may therefore share the
same effective channel.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

import numpy as np

from ic_quantum.core.validation import (
    validate_density_matrix,
    validate_kraus,
    validate_unitary,
)
from ic_quantum.dynamics.open_system import apply_kraus
from ic_quantum.dynamics.reversibility import (
    ReversibilityAssessment,
    assess_kraus_reversibility,
    assess_unitary_reversibility,
)


class LatentTransformKind(str, Enum):
    """Supported mathematical representations of an inter-depth transformation."""

    IDENTITY = "identity"
    UNITARY = "unitary"
    KRAUS_CPTP = "kraus_cptp"
    CUSTOM = "custom"


@dataclass(slots=True)
class LatentCausalTransform:
    """Effective transformation C_d acting between circuit depths d and d+1.

    CUSTOM is intentionally available for future non-Markovian or otherwise
    structured models. Such a model must provide an explicit callable and is not
    automatically assigned a reversibility class by the current infrastructure.
    """

    transform_id: str
    depth_after: int
    kind: LatentTransformKind
    dimension: int = 2
    agent_id: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    unitary: np.ndarray | None = None
    kraus_operators: tuple[np.ndarray, ...] | None = None
    custom_apply: Callable[[np.ndarray], np.ndarray] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.depth_after < 0:
            raise ValueError("depth_after must be non-negative.")
        if self.dimension <= 0:
            raise ValueError("dimension must be positive.")

        if self.kind is LatentTransformKind.IDENTITY:
            if any(
                value is not None
                for value in (self.unitary, self.kraus_operators, self.custom_apply)
            ):
                raise ValueError("Identity transformation must not define dynamics payloads.")
            return

        if self.kind is LatentTransformKind.UNITARY:
            if self.unitary is None:
                raise ValueError("Unitary latent transformation requires a unitary matrix.")
            matrix = np.asarray(self.unitary, dtype=complex)
            if matrix.shape != (self.dimension, self.dimension):
                raise ValueError("Unitary dimension does not match the declared dimension.")
            validate_unitary(matrix)
            self.unitary = matrix
            if self.kraus_operators is not None or self.custom_apply is not None:
                raise ValueError("Unitary transformation cannot also define Kraus/custom dynamics.")
            return

        if self.kind is LatentTransformKind.KRAUS_CPTP:
            if not self.kraus_operators:
                raise ValueError("Kraus latent transformation requires Kraus operators.")
            operators = tuple(np.asarray(k, dtype=complex) for k in self.kraus_operators)
            if any(k.shape != (self.dimension, self.dimension) for k in operators):
                raise ValueError("Kraus dimensions do not match the declared dimension.")
            validate_kraus(list(operators))
            self.kraus_operators = operators
            if self.unitary is not None or self.custom_apply is not None:
                raise ValueError("Kraus transformation cannot also define unitary/custom dynamics.")
            return

        if self.kind is LatentTransformKind.CUSTOM:
            if self.custom_apply is None:
                raise ValueError("Custom latent transformation requires custom_apply.")
            if self.unitary is not None or self.kraus_operators is not None:
                raise ValueError("Custom transformation cannot also define unitary/Kraus dynamics.")
            return

        raise ValueError(f"Unsupported latent-transform kind: {self.kind!r}")

    @property
    def interval(self) -> tuple[int, int]:
        """Return the circuit interval (d, d+1) represented by C_d."""
        return self.depth_after, self.depth_after + 1

    def apply(self, rho: np.ndarray) -> np.ndarray:
        """Apply the latent transformation to a valid density matrix."""
        validate_density_matrix(rho)
        if rho.shape != (self.dimension, self.dimension):
            raise ValueError("State dimension does not match latent transformation dimension.")

        if self.kind is LatentTransformKind.IDENTITY:
            return np.asarray(rho, dtype=complex).copy()

        if self.kind is LatentTransformKind.UNITARY:
            assert self.unitary is not None
            output = self.unitary @ rho @ self.unitary.conjugate().T
            validate_density_matrix(output)
            return output

        if self.kind is LatentTransformKind.KRAUS_CPTP:
            assert self.kraus_operators is not None
            return apply_kraus(rho, list(self.kraus_operators))

        assert self.custom_apply is not None
        output = np.asarray(self.custom_apply(rho), dtype=complex)
        validate_density_matrix(output)
        return output

    def reversibility_assessment(self) -> ReversibilityAssessment | None:
        """Classify reduced-map reversibility when the representation permits it."""
        if self.kind is LatentTransformKind.IDENTITY:
            return assess_unitary_reversibility(np.eye(self.dimension, dtype=complex))
        if self.kind is LatentTransformKind.UNITARY:
            assert self.unitary is not None
            return assess_unitary_reversibility(self.unitary)
        if self.kind is LatentTransformKind.KRAUS_CPTP:
            assert self.kraus_operators is not None
            return assess_kraus_reversibility(list(self.kraus_operators))
        return None

    def direct_unitary_inverse(self) -> np.ndarray | None:
        """Return the physical inverse gate only when C_d itself is unitary."""
        if self.kind is LatentTransformKind.IDENTITY:
            return np.eye(self.dimension, dtype=complex)
        if self.kind is LatentTransformKind.UNITARY:
            assert self.unitary is not None
            return self.unitary.conjugate().T
        return None
