import numpy as np
import pytest

from ic_quantum.core.states import REFERENCE_KETS, density_matrix
from ic_quantum.core.validation import (
    has_unit_trace,
    is_hermitian,
    is_positive_semidefinite,
    validate_density_matrix,
)


@pytest.mark.parametrize("ket", REFERENCE_KETS.values())
def test_reference_states_produce_valid_density_matrices(ket):
    rho = density_matrix(ket)
    assert is_hermitian(rho)
    assert has_unit_trace(rho)
    assert is_positive_semidefinite(rho)
    validate_density_matrix(rho)
    assert np.isclose(np.trace(rho @ rho), 1.0, atol=1e-10)
