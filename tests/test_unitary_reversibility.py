import numpy as np

from ic_quantum.agents.canonical import coherent_z_agent
from ic_quantum.core.states import reference_density
from ic_quantum.core.validation import is_unitary
from ic_quantum.dynamics.closed_system import apply_unitary, unitary_from_hamiltonian


def test_coherent_agent_is_directly_reversible():
    rho = reference_density("+")
    agent = coherent_z_agent(omega=1.0)
    unitary = unitary_from_hamiltonian(agent.interaction_hamiltonian, time=0.7)
    assert is_unitary(unitary)

    perturbed = apply_unitary(rho, unitary)
    recovered = apply_unitary(perturbed, unitary.conjugate().T)

    assert np.allclose(recovered, rho, atol=1e-10, rtol=0.0)
