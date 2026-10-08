"""Final validated causal-agent catalog used by the IC final dataset."""

from __future__ import annotations

from ic_quantum.data.causal_agent_schema import (
    CausalAgentModelRecord,
    DynamicRegime,
    FieldStatus,
    MathematicalField,
    MemoryRegime,
    ModelMaturityLevel,
    ParameterSpec,
    ProvenanceKind,
    ProvenanceRecord,
)
from ic_quantum.data.initial_catalog import (
    coherent_detuning_model,
    finite_exchange_relaxation_model,
)
from ic_quantum.data.registry import CausalAgentRegistry


def _landi_spin_boson_reference() -> ProvenanceRecord:
    return ProvenanceRecord(
        kind=ProvenanceKind.LITERATURE_DERIVED,
        publication="Quantum Information and Quantum Noise",
        authors=("Gabriel T. Landi",),
        year=2019,
        locator=(
            "Sec. 6.8, Eqs. (6.156), (6.160), (6.169)-(6.172), (6.177): "
            "longitudinal spin-boson pure dephasing"
        ),
        assumptions=(
            "initial system-bath product state",
            "thermal bosonic bath",
            "natural units hbar = k_B = 1 in the implemented parameterization",
            "finite-mode discretization Omega_k=k*Omega_c/N and lambda_k=sqrt(Omega_k/N)",
        ),
        ic_interpretation=(
            "Used as an explicit physical dephasing family. Finite mode count is retained "
            "so coherence revivals and memory can occur; the effective dephasing channel "
            "is treated as an output of the source model, not its causal identity."
        ),
    )


def _norambuena_photon_reference() -> ProvenanceRecord:
    return ProvenanceRecord(
        kind=ProvenanceKind.LITERATURE_DERIVED,
        publication=(
            "Coding closed and open quantum systems in MATLAB: "
            "applications in quantum optics and condensed matter"
        ),
        authors=("Ariel Norambuena", "Diego Tancara", "Raul Coto"),
        year=2020,
        locator=(
            "Sec. 2, Eq. (10): Jaynes-Cummings light-matter interaction; "
            "Sec. 3.2, Eq. (21): Markovian two-level system coupled to a photon reservoir"
        ),
        assumptions=(
            "rotating-wave light-matter interaction for the microscopic interpretation",
            "Markovian reduced dynamics",
            "zero-temperature Nph=0 and undriven Omega=0 specialization in this IC family",
            "weak-coupling reservoir approximation for the reduced semigroup",
        ),
        ic_interpretation=(
            "The IC specializes Eq. (21) to the undriven zero-temperature radiative "
            "decay semigroup. The multimode interaction expression is the standard "
            "reservoir extension of the Jaynes-Cummings exchange in Eq. (10)."
        ),
    )


def _author_derivation(note: str) -> ProvenanceRecord:
    return ProvenanceRecord(kind=ProvenanceKind.AUTHOR_DERIVED, note=note)


def finite_mode_spin_boson_dephasing_model() -> CausalAgentModelRecord:
    literature = _landi_spin_boson_reference()
    derived = _author_derivation(
        "The Kraus pair with q(t)=exp[-Lambda(t)] is used as an equivalent one-qubit "
        "representation of the exact coherence attenuation in the cited model."
    )
    return CausalAgentModelRecord(
        agent_id="finite-mode-spin-boson-dephasing",
        provisional_name="Finite-mode longitudinal spin-boson dephasing",
        physical_category="bosonic_bath_longitudinal_dephasing",
        physical_description=(
            "A qubit couples longitudinally through sigma_z to a finite thermal set "
            "of bosonic modes. The interaction changes coherences without changing "
            "computational-basis populations and may exhibit finite-bath revivals."
        ),
        target_system="single qubit",
        physical_source="finite thermal bosonic bath",
        causal_mechanism="longitudinal sigma_z coupling to thermally populated bosonic modes",
        relevant_degrees_of_freedom=("system spin/qubit", "finite bosonic bath modes"),
        coupling_mechanism="longitudinal sigma_z displacement of bosonic modes",
        system_hamiltonian=MathematicalField(
            status=FieldStatus.VALUE,
            expression="H_S = (hbar*omega/2) sigma_z",
            provenance=(literature,),
        ),
        agent_hamiltonian=MathematicalField(
            status=FieldStatus.VALUE,
            expression="H_A = sum_k hbar*Omega_k b_k^dagger b_k",
            provenance=(literature,),
        ),
        interaction_hamiltonian=MathematicalField(
            status=FieldStatus.VALUE,
            expression="H_int = sum_k hbar*lambda_k sigma_z (b_k + b_k^dagger)",
            provenance=(literature,),
        ),
        parameters=(
            ParameterSpec(
                name="mode_count",
                symbol="N",
                unit="1",
                physical_range="positive integer; final dataset uses a documented finite grid",
                description="Number of explicitly retained bosonic bath modes.",
                provenance=(literature,),
            ),
            ParameterSpec(
                name="cutoff_angular_frequency",
                symbol="Omega_c",
                unit="rad s^-1",
                physical_range="Omega_c > 0",
                description="Upper angular-frequency cutoff of the finite mode grid.",
                provenance=(literature,),
            ),
            ParameterSpec(
                name="temperature_angular_frequency",
                symbol="T",
                unit="rad s^-1",
                physical_range="T >= 0 in natural units k_B=hbar=1",
                description="Thermal energy expressed as an angular-frequency scale.",
                provenance=(literature,),
            ),
            ParameterSpec(
                name="interaction_time",
                symbol="t",
                unit="s",
                physical_range="t >= 0",
                description="System-bath interaction time.",
                provenance=(literature,),
            ),
        ),
        initial_agent_state=MathematicalField(
            status=FieldStatus.VALUE,
            expression="rho_A(0) = exp(-H_A/T) / Z_A",
            provenance=(literature,),
        ),
        assumptions=(
            "initial product state",
            "thermal finite bosonic bath",
            "longitudinal coupling commuting with H_S",
            "natural units hbar=k_B=1 for the finite-mode parameter formulas",
        ),
        dynamic_regime=DynamicRegime.INCOHERENT_CPTP,
        memory_regime=MemoryRegime.MIXED_OR_CROSSOVER,
        temporal_description=(
            "rho_01(t)=rho_01(0) exp[-Lambda(t)], with exact finite-mode Lambda(t); "
            "finite N may produce coherence revivals"
        ),
        kraus_operators=MathematicalField(
            status=FieldStatus.VALUE,
            expression=(
                "K0=sqrt((1+q(t))/2) I; K1=sqrt((1-q(t))/2) sigma_z; "
                "q(t)=exp[-Lambda(t)]"
            ),
            provenance=(derived, literature),
        ),
        effective_dynamics=MathematicalField(
            status=FieldStatus.VALUE,
            expression=(
                "rho_00(t)=rho_00(0), rho_11(t)=rho_11(0), "
                "rho_01(t)=exp[-Lambda(t)] rho_01(0)"
            ),
            provenance=(literature,),
        ),
        observables=("X", "Y", "Z"),
        information_metrics=(
            "von_neumann_entropy", "purity", "l1_coherence", "fidelity",
            "trace_distance", "bloch_vector", "coherence_factor", "choi_rank"
        ),
        reversibility_class="parameter_and_time_dependent_reduced_dephasing",
        validity_domain=(
            "single qubit",
            "finite thermal bosonic mode model of Sec. 6.8",
            "longitudinal pure-dephasing coupling",
        ),
        references=(literature, derived),
        derivation_method=(
            "exact finite-mode spin-boson coherence exponent followed by its "
            "equivalent one-qubit dephasing Kraus representation"
        ),
        validation_method=(
            "verify Lambda(0)=0 and identity at t=0",
            "verify computational-basis populations are invariant",
            "verify Kraus completeness for every sampled parameter point",
            "compare Kraus evolution against the analytical matrix-element map",
            "verify exact finite-mode recurrence for commensurate mode frequencies",
        ),
        maturity_level=ModelMaturityLevel.LEVEL_3,
        notes=(
            "Finite-mode revivals are treated as model-specific memory evidence, not "
            "as a universal statement about every dephasing source.",
        ),
    )


def markovian_photon_reservoir_decay_model() -> CausalAgentModelRecord:
    literature = _norambuena_photon_reference()
    derived = _author_derivation(
        "For the zero-temperature undriven Markovian specialization, the excited "
        "population e^{-gamma t} is represented by amplitude damping with "
        "p(t)=1-e^{-gamma t}."
    )
    return CausalAgentModelRecord(
        agent_id="markovian-photon-reservoir-decay",
        provisional_name="Markovian radiative decay into a photon reservoir",
        physical_category="radiative_markovian_relaxation",
        physical_description=(
            "A two-level system exchanges excitations with electromagnetic/photon "
            "reservoir modes; after the Markovian weak-coupling reduction at zero "
            "temperature the excited population decays exponentially."
        ),
        target_system="single qubit/two-level system",
        physical_source="electromagnetic photon reservoir",
        causal_mechanism="rotating-wave excitation exchange followed by Markovian reservoir reduction",
        relevant_degrees_of_freedom=("two-level system", "photon reservoir modes"),
        coupling_mechanism="rotating-wave excitation exchange with photon modes",
        system_hamiltonian=MathematicalField(
            status=FieldStatus.VALUE,
            expression="H_S = hbar*omega_0 sigma_+ sigma_-",
            provenance=(literature,),
        ),
        agent_hamiltonian=MathematicalField(
            status=FieldStatus.VALUE,
            expression="H_A = sum_k hbar*omega_k a_k^dagger a_k",
            provenance=(literature,),
        ),
        interaction_hamiltonian=MathematicalField(
            status=FieldStatus.VALUE,
            expression=(
                "H_int = hbar sum_k g_k (sigma_+ a_k + sigma_- a_k^dagger)"
            ),
            provenance=(literature,),
        ),
        parameters=(
            ParameterSpec(
                name="decay_rate",
                symbol="gamma",
                unit="s^-1",
                physical_range="gamma >= 0",
                description="Effective Markovian radiative decay rate.",
                provenance=(literature,),
            ),
            ParameterSpec(
                name="interaction_time",
                symbol="t",
                unit="s",
                physical_range="t >= 0",
                description="Elapsed reduced-dynamics time.",
                provenance=(literature,),
            ),
        ),
        initial_agent_state=MathematicalField(
            status=FieldStatus.VALUE,
            expression="rho_A(0)=|vacuum><vacuum| (N_ph=0 specialization)",
            provenance=(literature,),
        ),
        assumptions=(
            "zero-temperature photon occupation Nph=0",
            "undriven limit Omega=0",
            "weak-coupling Markovian reservoir reduction",
            "rotating-wave excitation-exchange interpretation",
        ),
        dynamic_regime=DynamicRegime.INCOHERENT_CPTP,
        memory_regime=MemoryRegime.MARKOVIAN,
        temporal_description=(
            "rho_11(t)=exp(-gamma t) rho_11(0); "
            "effective amplitude-damping p(t)=1-exp(-gamma t)"
        ),
        master_equation=MathematicalField(
            status=FieldStatus.VALUE,
            expression=(
                "d rho/dt = gamma [sigma_- rho sigma_+ "
                "- 1/2 {sigma_+ sigma_-, rho}]"
            ),
            provenance=(literature,),
        ),
        kraus_operators=MathematicalField(
            status=FieldStatus.VALUE,
            expression=(
                "K0=diag(1,exp(-gamma t/2)); "
                "K1=[[0,sqrt(1-exp(-gamma t))],[0,0]]"
            ),
            provenance=(derived, literature),
        ),
        effective_dynamics=MathematicalField(
            status=FieldStatus.VALUE,
            expression="E_t = amplitude_damping[p(t)=1-exp(-gamma t)]",
            provenance=(derived, literature),
        ),
        observables=("X", "Y", "Z"),
        information_metrics=(
            "von_neumann_entropy", "purity", "l1_coherence", "fidelity",
            "trace_distance", "bloch_vector", "choi_rank"
        ),
        reversibility_class="parameter_and_time_dependent_reduced_relaxation",
        validity_domain=(
            "single two-level system",
            "zero-temperature undriven specialization",
            "Markovian weak-coupling regime",
        ),
        references=(literature, derived),
        derivation_method=(
            "literature Markovian photon-reservoir master equation specialized to "
            "Nph=0 and Omega=0; analytical semigroup mapped to Kraus form"
        ),
        validation_method=(
            "verify p(0)=0 and identity at zero time/rate",
            "verify excited population follows exp(-gamma t)",
            "verify Kraus completeness and CPTP output",
            "compare against direct analytical population/coherence solution",
        ),
        maturity_level=ModelMaturityLevel.LEVEL_3,
        notes=(
            "This family can share the same effective amplitude-damping channel as "
            "the finite two-level exchange model at matched p, despite distinct source models.",
        ),
    )


def build_final_registry() -> CausalAgentRegistry:
    registry = CausalAgentRegistry()
    registry.add(coherent_detuning_model())
    registry.add(finite_exchange_relaxation_model())
    registry.add(finite_mode_spin_boson_dephasing_model())
    registry.add(markovian_photon_reservoir_decay_model())
    return registry
