"""Canonical causal-agent models used only as controlled scientific baselines."""

from __future__ import annotations

from ic_quantum.agents.base import CausalAgent
from ic_quantum.channels.amplitude_damping import amplitude_damping_kraus
from ic_quantum.channels.dephasing import dephasing_kraus
from ic_quantum.channels.depolarizing import depolarizing_kraus
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


def dephasing_agent(p: float) -> CausalAgent:
    return CausalAgent(
        agent_id="dephasing",
        name="Pure dephasing channel",
        physical_model="Canonical reduced open-system model",
        dynamic_regime="nonunitary_cptp",
        parameters={"p": float(p)},
        kraus_operators=dephasing_kraus(p),
        effective_channel="pure_dephasing",
        reversibility_class="no_global_CPTP_inverse_unless_unitary",
    )


def amplitude_damping_agent(p: float) -> CausalAgent:
    return CausalAgent(
        agent_id="amplitude_damping",
        name="Amplitude damping channel",
        physical_model="Canonical energy-relaxation model",
        dynamic_regime="nonunitary_cptp",
        parameters={"p": float(p)},
        kraus_operators=amplitude_damping_kraus(p),
        effective_channel="amplitude_damping",
        reversibility_class="no_global_CPTP_inverse_unless_unitary",
    )


def depolarizing_agent(p: float) -> CausalAgent:
    return CausalAgent(
        agent_id="depolarizing",
        name="Depolarizing channel",
        physical_model="Canonical isotropic reduced-noise model",
        dynamic_regime="nonunitary_cptp",
        parameters={"p": float(p)},
        kraus_operators=depolarizing_kraus(p),
        effective_channel="depolarizing",
        reversibility_class="no_global_CPTP_inverse_unless_unitary",
    )
