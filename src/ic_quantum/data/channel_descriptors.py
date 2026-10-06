"""Universal channel descriptors inferable from process characterization."""

from __future__ import annotations

import numpy as np

from ic_quantum.dynamics.reversibility import (
    assess_kraus_reversibility,
    assess_unitary_reversibility,
    choi_from_superoperator,
    superoperator_from_kraus,
    superoperator_from_unitary,
)


def _describe_superoperator(superoperator: np.ndarray, dimension: int) -> dict[str, object]:
    choi = choi_from_superoperator(superoperator, dimension)
    choi_h = 0.5 * (choi + choi.conjugate().T)
    choi_eigs = np.linalg.eigvalsh(choi_h).real
    singular_values = np.linalg.svd(superoperator, compute_uv=False).real
    normalized_choi = choi_h / float(dimension)
    return {
        "choi_eigenvalues": [float(v) for v in np.sort(choi_eigs)],
        "choi_trace": float(np.real(np.trace(choi_h))),
        "normalized_choi_purity": float(
            np.real(np.trace(normalized_choi @ normalized_choi))
        ),
        "superoperator_singular_values": [
            float(v) for v in np.sort(singular_values)[::-1]
        ],
        "superoperator_determinant_abs": float(abs(np.linalg.det(superoperator))),
    }


def _assessment_dict(assessment) -> dict[str, object]:
    return {
        "is_cptp": assessment.is_cptp,
        "linear_invertible": assessment.linear_invertible,
        "inverse_cptp": assessment.inverse_cptp,
        "direct_unitary_inverse": assessment.direct_unitary_inverse,
        "choi_rank": assessment.choi_rank,
        "condition_number": assessment.condition_number,
        "reversibility_class": assessment.classification,
    }


def describe_kraus_channel(kraus_ops: list[np.ndarray]) -> tuple[dict[str, object], dict[str, object]]:
    assessment = assess_kraus_reversibility(kraus_ops)
    superoperator = superoperator_from_kraus(kraus_ops)
    universal = _describe_superoperator(superoperator, kraus_ops[0].shape[0])
    return _assessment_dict(assessment), universal


def describe_unitary_channel(unitary: np.ndarray) -> tuple[dict[str, object], dict[str, object]]:
    assessment = assess_unitary_reversibility(unitary)
    superoperator = superoperator_from_unitary(unitary)
    universal = _describe_superoperator(superoperator, unitary.shape[0])
    return _assessment_dict(assessment), universal
