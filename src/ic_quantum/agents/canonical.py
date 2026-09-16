"""Canonical causal-agent models used only as controlled scientific baselines."""

from __future__ import annotations

from ic_quantum.agents.base import CausalAgent
from ic_quantum.channels.unitary import coherent_z_hamiltonian


def coherent_z_agent(omega: float, hbar: float = 1.0) -> CausalAgent:
    return CausalAgent(
        agent_id="coherent_z",
        name="Coherent Z perturbation",
        physical_model="Controlled Hamiltonian baseline",
        dynamic_regime="unitary_coherent",
        parameters={"omega": float(omega), "hbar": float(hbar)},
        interaction_hamiltonian=coherent_z_hamiltonian(omega, hbar),
        effective_channel="rho -> U rho U^dagger",
        reversibility_class="direct_unitary_inverse",
    )
