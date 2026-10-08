"""Initial validated causal-agent catalog."""

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
from ic_quantum.data.registry import CausalAgentRegistry


def _author_record(note: str) -> ProvenanceRecord:
    return ProvenanceRecord(kind=ProvenanceKind.AUTHOR_DERIVED, note=note)


def _maziero_reference() -> ProvenanceRecord:
    return ProvenanceRecord(
        kind=ProvenanceKind.LITERATURE_DERIVED,
        publication="A representação de Kraus para a dinâmica de sistemas quânticos abertos",
        authors=("Jonas Maziero",),
        year=2016,
        locator="Sec. II: joint unitary evolution and partial trace",
        assumptions=(
            "system plus environment treated as a closed system",
            "initial system-environment product state in the didactic derivation",
        ),
        ic_interpretation=(
            "Used for the microscopic-to-reduced modeling principle. The finite "
            "two-level exchange model below is an IC controlled instantiation, not "
            "claimed to be the article's exact electromagnetic-vacuum model."
        ),
    )


def coherent_detuning_model() -> CausalAgentModelRecord:
    source = _author_record(
        "Controlled coherent baseline interpreted as a longitudinal frequency offset."
    )
    return CausalAgentModelRecord(
        agent_id="coherent-longitudinal-detuning",
        provisional_name="Coherent longitudinal detuning",
        physical_category="coherent_control_or_frequency_offset",
        physical_description=(
            "A systematic longitudinal frequency offset acting on a single qubit "
            "during a finite interaction window."
        ),
        target_system="single qubit",
        physical_source="systematic coherent frequency offset or control-field detuning",
        causal_mechanism="longitudinal modulation of the qubit splitting through sigma_z",
        relevant_degrees_of_freedom=("qubit", "frequency offset"),
        coupling_mechanism="effective longitudinal sigma_z Hamiltonian",
        interaction_hamiltonian=MathematicalField(
            status=FieldStatus.VALUE,
            expression="H_int = (hbar * delta_omega / 2) sigma_z",
            provenance=(source,),
        ),
        parameters=(
            ParameterSpec(
                name="delta_omega",
                symbol="delta_omega",
                unit="rad s^-1",
                physical_range="real; bounded by the chosen experiment",
                description="Angular-frequency detuning.",
                provenance=(source,),
            ),
            ParameterSpec(
                name="interaction_time",
                symbol="t",
                unit="s",
                physical_range="t >= 0",
                description="Duration of the perturbation.",
                provenance=(source,),
            ),
        ),
        assumptions=(
            "time-independent perturbation over the interaction window",
            "closed/effectively coherent reduced dynamics",
        ),
        dynamic_regime=DynamicRegime.COHERENT_UNITARY,
        memory_regime=MemoryRegime.NOT_APPLICABLE,
        temporal_description="U(t)=exp[-i H_int t/hbar]",
        unitary_transform=MathematicalField(
            status=FieldStatus.VALUE,
            expression="U(t)=exp[-i H_int t/hbar]",
            provenance=(source,),
        ),
        effective_dynamics=MathematicalField(
            status=FieldStatus.VALUE,
            expression="E_t(rho)=U(t) rho U(t)^dagger",
            provenance=(source,),
        ),
        observables=("X", "Y", "Z"),
        information_metrics=(
            "von_neumann_entropy", "purity", "l1_coherence", "fidelity", "bloch_vector"
        ),
        reversibility_class="direct_unitary_inverse",
        validity_domain=("single-qubit coherent regime",),
        references=(source,),
        derivation_method="unitary evolution from a constant Hamiltonian",
        validation_method=(
            "verify H=H^dagger",
            "verify U^dagger U=I",
            "recover probe states with U^dagger",
        ),
        maturity_level=ModelMaturityLevel.LEVEL_3,
        notes=("Positive-control baseline for reversibility.",),
    )


def finite_exchange_relaxation_model() -> CausalAgentModelRecord:
    author = _author_record(
        "Finite two-level exchange model introduced as a controlled microscopic "
        "instantiation; p(t)=sin^2(g t) is derived from its joint unitary."
    )
    literature = _maziero_reference()
    return CausalAgentModelRecord(
        agent_id="finite-two-level-exchange-relaxation",
        provisional_name="Finite two-level exchange relaxation agent",
        physical_category="finite_quantum_environment_relaxation",
        physical_description=(
            "A two-level external degree of freedom starts in |0> and exchanges one "
            "excitation coherently with the system. Discarding it produces reduced relaxation."
        ),
        target_system="single qubit",
        physical_source="finite external two-level quantum degree of freedom",
        causal_mechanism="coherent single-excitation exchange followed by discarding the external degree of freedom",
        relevant_degrees_of_freedom=("system qubit", "two-level causal agent"),
        coupling_mechanism="single-excitation exchange",
        interaction_hamiltonian=MathematicalField(
            status=FieldStatus.VALUE,
            expression="H_int = i*hbar*g(|01><10| - |10><01|)",
            provenance=(author,),
        ),
        parameters=(
            ParameterSpec(
                name="coupling",
                symbol="g",
                unit="rad s^-1",
                physical_range="g >= 0 for the canonical parameterization",
                description="System-agent excitation-exchange coupling rate.",
                provenance=(author,),
            ),
            ParameterSpec(
                name="interaction_time",
                symbol="t",
                unit="s",
                physical_range="t >= 0",
                description="Interaction duration.",
                provenance=(author,),
            ),
        ),
        initial_agent_state=MathematicalField(
            status=FieldStatus.VALUE,
            expression="rho_A(0)=|0><0|",
            provenance=(author, literature),
        ),
        assumptions=(
            "initial product state rho_S tensor |0><0|_A",
            "finite two-level agent",
            "joint closed evolution during the modeled interval",
        ),
        dynamic_regime=DynamicRegime.INCOHERENT_CPTP,
        memory_regime=MemoryRegime.MIXED_OR_CROSSOVER,
        temporal_description=(
            "U_SA(t)=exp[-i H_int t/hbar], rho_S(t)=Tr_A[U_SA rho_SA U_SA^dagger]"
        ),
        kraus_operators=MathematicalField(
            status=FieldStatus.VALUE,
            expression="K0=diag(1,cos(g t)); K1=[[0,sin(g t)],[0,0]]; p(t)=sin^2(g t)",
            provenance=(author,),
        ),
        unitary_transform=MathematicalField(
            status=FieldStatus.VALUE,
            expression="U_SA(t)=exp[-i H_int t/hbar]",
            provenance=(author, literature),
        ),
        effective_dynamics=MathematicalField(
            status=FieldStatus.VALUE,
            expression="E_t(rho)=Tr_A[U_SA(t)(rho tensor |0><0|)U_SA(t)^dagger]",
            provenance=(author, literature),
        ),
        observables=("X", "Y", "Z"),
        information_metrics=(
            "von_neumann_entropy", "purity", "l1_coherence", "fidelity",
            "bloch_vector", "choi_rank"
        ),
        reversibility_class="reduced_nonunitary_model_dependent_recovery",
        validity_domain=("finite two-level agent initialized in |0>", "single system qubit"),
        references=(author, literature),
        derivation_method=(
            "joint unitary evolution followed by partial trace; reduced Kraus form "
            "derived from the finite exchange unitary"
        ),
        validation_method=(
            "verify H=H^dagger",
            "verify U^dagger U=I",
            "verify Kraus completeness",
            "compare reduced joint dynamics against amplitude-damping Kraus dynamics "
            "for all six standardized probe states",
        ),
        maturity_level=ModelMaturityLevel.LEVEL_3,
        notes=(
            "Do not relabel this finite controlled model as electromagnetic-vacuum "
            "spontaneous emission without a source-specific derivation.",
        ),
    )


def build_initial_registry() -> CausalAgentRegistry:
    registry = CausalAgentRegistry()
    registry.add(coherent_detuning_model())
    registry.add(finite_exchange_relaxation_model())
    return registry
