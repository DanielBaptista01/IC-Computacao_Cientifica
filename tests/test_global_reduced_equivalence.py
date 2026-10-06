import numpy as np

from ic_quantum.channels.amplitude_damping import (
    amplitude_damping_dilation_unitary,
    amplitude_damping_kraus,
)
from ic_quantum.core.states import reference_density
from ic_quantum.core.validation import is_unitary
from ic_quantum.dynamics.closed_system import apply_unitary
from ic_quantum.dynamics.open_system import apply_kraus
from ic_quantum.dynamics.partial_trace import partial_trace_bipartite


def test_global_unitary_dilation_matches_reduced_amplitude_damping():
    p = 0.25
    rho_s = reference_density("+")
    rho_a = reference_density("0")
    rho_sa = np.kron(rho_s, rho_a)

    unitary_sa = amplitude_damping_dilation_unitary(p)
    assert is_unitary(unitary_sa)
    global_output = apply_unitary(rho_sa, unitary_sa)
    reduced_output = partial_trace_bipartite(global_output, dims=(2, 2), trace_out="B")
    kraus_output = apply_kraus(rho_s, amplitude_damping_kraus(p))

    assert np.allclose(reduced_output, kraus_output, atol=1e-10, rtol=0.0)
