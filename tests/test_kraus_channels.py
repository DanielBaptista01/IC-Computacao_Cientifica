import numpy as np
import pytest

from ic_quantum.channels.amplitude_damping import amplitude_damping_kraus
from ic_quantum.channels.dephasing import dephasing_kraus
from ic_quantum.channels.depolarizing import depolarizing_kraus
from ic_quantum.core.states import reference_density
from ic_quantum.core.validation import kraus_completeness, validate_density_matrix
from ic_quantum.dynamics.open_system import apply_kraus
from ic_quantum.metrics.coherence import l1_coherence


@pytest.mark.parametrize(
    "factory,p",
    [
        (dephasing_kraus, 0.35),
        (amplitude_damping_kraus, 0.25),
        (depolarizing_kraus, 0.20),
    ],
)
def test_kraus_channels_are_trace_preserving_and_output_valid_states(factory, p):
    operators = factory(p)
    assert kraus_completeness(operators)
    output = apply_kraus(reference_density("+"), operators)
    validate_density_matrix(output)
    assert np.isclose(np.trace(output), 1.0, atol=1e-10)


def test_dephasing_reduces_l1_coherence_of_plus_state():
    rho = reference_density("+")
    output = apply_kraus(rho, dephasing_kraus(0.35))
    assert l1_coherence(output) < l1_coherence(rho)
    assert np.isclose(l1_coherence(output), 0.65, atol=1e-10)
