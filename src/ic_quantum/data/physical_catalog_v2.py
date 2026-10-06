"""Validated physical-source causal-agent catalog for the v2 expansion."""

from __future__ import annotations

from ic_quantum.data.causal_agent_schema import (
    CausalAgentModelRecord, DynamicRegime, FieldStatus, MathematicalField,
    MemoryRegime, ModelMaturityLevel, ParameterSpec, ProvenanceKind, ProvenanceRecord,
)
from ic_quantum.data.final_catalog import build_final_registry
from ic_quantum.data.registry import CausalAgentRegistry


def _norambuena() -> ProvenanceRecord:
    return ProvenanceRecord(
        kind=ProvenanceKind.LITERATURE_DERIVED,
        publication="Coding closed and open quantum systems in MATLAB: applications in quantum optics and condensed matter",
        authors=("Ariel Norambuena","Diego Tancara","Raul Coto"),
        year=2020,
        locator="Sec. 2 light-matter/Jaynes-Cummings model; Sec. 3.2 Eq. (21) driven two-level system with photon reservoir",
        assumptions=("two-level system","rotating-wave/light-matter reduction","Markovian reservoir when Eq. (21) is used"),
        ic_interpretation="Used to ground coherent electromagnetic driving and finite-temperature photon-reservoir dynamics; effective parameters are kept distinct from source identity.",
    )


def _landi() -> ProvenanceRecord:
    return ProvenanceRecord(
        kind=ProvenanceKind.LITERATURE_DERIVED,
        publication="Quantum Information and Quantum Noise",
        authors=("Gabriel T. Landi",),
        year=2019,
        locator="Sec. 6.8 longitudinal spin-boson pure-dephasing model",
        assumptions=("bosonic harmonic modes","initial product state","thermal oscillator state for reduced dephasing"),
        ic_interpretation="Specialized to one explicitly identified mechanical/phonon-like mode; this is a generic oscillator model, not a hardware-specific strain calibration.",
    )


def _author(note: str) -> ProvenanceRecord:
    return ProvenanceRecord(kind=ProvenanceKind.AUTHOR_DERIVED, note=note)


def external_electromagnetic_drive_model() -> CausalAgentModelRecord:
    lit=_norambuena()
    deriv=_author("Semiclassical near-resonant external electromagnetic field represented in the rotating frame/RWA by Delta sigma_z + Omega(cos(phi)sigma_x+sin(phi)sigma_y). Omega absorbs the platform-specific dipole-field transduction.")
    return CausalAgentModelRecord(
        agent_id="external-electromagnetic-rabi-drive",
        provisional_name="External coherent electromagnetic Rabi drive",
        physical_category="external_electromagnetic_field",
        physical_description="An unintended coherent electromagnetic wave couples to a two-level transition and produces a deterministic rotation whose axis depends on drive phase and detuning.",
        target_system="single effective qubit/two-level transition",
        relevant_degrees_of_freedom=("qubit","classical electromagnetic drive"),
        coupling_mechanism="electric/magnetic dipole coupling reduced to an effective near-resonant Rabi Hamiltonian",
        system_hamiltonian=MathematicalField(FieldStatus.VALUE,"H_S=(hbar*omega_0/2) sigma_z",(lit,)),
        agent_hamiltonian=MathematicalField(FieldStatus.NOT_APPLICABLE),
        interaction_hamiltonian=MathematicalField(
            FieldStatus.VALUE,
            "H_RWA=(hbar/2)[Delta sigma_z + Omega(cos(phi)sigma_x+sin(phi)sigma_y)]",
            (lit,deriv),
        ),
        parameters=(
            ParameterSpec("rabi_rate","Omega","rad s^-1","Omega >= 0","Effective field-qubit coupling rate; platform-specific dipole matrix element is absorbed here.",(lit,deriv)),
            ParameterSpec("detuning","Delta","rad s^-1","real","Drive-transition angular-frequency detuning.",(lit,deriv)),
            ParameterSpec("phase","phi","rad","[0,2*pi)","Drive phase setting the transverse rotation axis.",(deriv,)),
            ParameterSpec("interaction_time","t","s","t >= 0","Exposure duration.",(deriv,)),
        ),
        assumptions=("semiclassical coherent field","rotating-wave/near-resonant effective model","single two-level transition","no stochastic amplitude/phase noise in this validated family"),
        dynamic_regime=DynamicRegime.COHERENT_UNITARY,
        memory_regime=MemoryRegime.NOT_APPLICABLE,
        temporal_description="U(t)=exp[-i H_RWA t/hbar]",
        unitary_transform=MathematicalField(FieldStatus.VALUE,"U(t)=exp[-i H_RWA t/hbar]",(lit,deriv)),
        effective_dynamics=MathematicalField(FieldStatus.VALUE,"E_t(rho)=U(t)rho U(t)^dagger",(deriv,)),
        observables=("X","Y","Z"),
        information_metrics=("von_neumann_entropy","purity","l1_coherence","fidelity","trace_distance","bloch_vector"),
        reversibility_class="direct_unitary_inverse",
        validity_domain=("single effective qubit","coherent external field","RWA/rotating-frame regime"),
        references=(lit,deriv),
        derivation_method="semiclassical light-matter coupling reduced to time-independent rotating-frame Hamiltonian",
        validation_method=("verify Hermiticity","verify U^dagger U=I","verify resonant Rabi transition probability","verify inverse U^dagger"),
        maturity_level=ModelMaturityLevel.LEVEL_3,
        notes=("Raw E-field amplitude is not inferred without a platform-specific dipole matrix element; Omega is therefore retained as the physically effective coupling parameter.",),
    )


def external_magnetic_zeeman_model() -> CausalAgentModelRecord:
    deriv=_author("Physical-source specialization requested by the IC: magnetic-dipole/Zeeman coupling H=(hbar gamma/2) B dot sigma. Numerical validation covers arbitrary field orientation. Dataset uses an electron-spin-like gamma only as an explicitly marked theoretical reference, not hardware calibration.")
    return CausalAgentModelRecord(
        agent_id="external-magnetic-zeeman-field",
        provisional_name="External magnetic-field Zeeman perturbation",
        physical_category="external_magnetic_field",
        physical_description="A static or piecewise-constant external magnetic field changes the effective spin Hamiltonian, producing phase shifts for longitudinal components and transitions for transverse components.",
        target_system="effective spin-1/2 qubit",
        relevant_degrees_of_freedom=("effective spin","external magnetic field"),
        coupling_mechanism="Zeeman magnetic-dipole coupling",
        interaction_hamiltonian=MathematicalField(FieldStatus.VALUE,"H_int=(hbar*gamma/2)(B_x sigma_x+B_y sigma_y+B_z sigma_z)",(deriv,)),
        parameters=(
            ParameterSpec("field_x","B_x","T","real","Magnetic-field x component.",(deriv,)),
            ParameterSpec("field_y","B_y","T","real","Magnetic-field y component.",(deriv,)),
            ParameterSpec("field_z","B_z","T","real","Magnetic-field z component.",(deriv,)),
            ParameterSpec("gyromagnetic_ratio","gamma","rad s^-1 T^-1","gamma > 0","Platform-dependent gyromagnetic ratio.",(deriv,)),
            ParameterSpec("interaction_time","t","s","t >= 0","Field exposure duration.",(deriv,)),
        ),
        assumptions=("effective spin-1/2 description","piecewise-constant classical magnetic field","no field stochasticity in this validated family"),
        dynamic_regime=DynamicRegime.COHERENT_UNITARY,
        memory_regime=MemoryRegime.NOT_APPLICABLE,
        temporal_description="U(t)=exp[-i H_int t/hbar]",
        unitary_transform=MathematicalField(FieldStatus.VALUE,"U(t)=exp[-i H_int t/hbar]",(deriv,)),
        effective_dynamics=MathematicalField(FieldStatus.VALUE,"E_t(rho)=U(t)rho U(t)^dagger",(deriv,)),
        observables=("X","Y","Z"),
        information_metrics=("von_neumann_entropy","purity","l1_coherence","fidelity","trace_distance","bloch_vector"),
        reversibility_class="direct_unitary_inverse",
        validity_domain=("effective spin-1/2","classical field approximately constant over each simulated interval"),
        references=(deriv,),
        derivation_method="direct Zeeman Hamiltonian evolution",
        validation_method=("verify Hermiticity","verify unitarity","verify longitudinal field preserves populations","verify transverse pi rotation swaps computational populations"),
        maturity_level=ModelMaturityLevel.LEVEL_3,
        notes=("A stochastic magnetic-noise spectrum is not claimed by this model; it quantifies the coherent field component only.",),
    )


def thermal_photon_reservoir_model() -> CausalAgentModelRecord:
    lit=_norambuena()
    deriv=_author("Finite-temperature specialization of the standard Markovian photon-reservoir master equation. The exact semigroup is represented as generalized amplitude damping.")
    return CausalAgentModelRecord(
        agent_id="thermal-photon-reservoir",
        provisional_name="Finite-temperature Markovian photon reservoir",
        physical_category="thermal_electromagnetic_reservoir",
        physical_description="A thermal photon bath drives both downward relaxation and upward excitation of a two-level system, with Bose occupation set by transition frequency and temperature.",
        target_system="single two-level system",
        relevant_degrees_of_freedom=("two-level system","thermal photon reservoir modes"),
        coupling_mechanism="rotating-wave excitation exchange with thermally populated photon modes",
        interaction_hamiltonian=MathematicalField(FieldStatus.VALUE,"H_int=hbar sum_k g_k(sigma_+ a_k + sigma_- a_k^dagger)",(lit,)),
        parameters=(
            ParameterSpec("decay_rate","gamma","s^-1","gamma >= 0","Zero-temperature spontaneous-emission scale entering the thermal Lindblad rates.",(lit,)),
            ParameterSpec("transition_angular_frequency","omega_0","rad s^-1","omega_0 > 0","Two-level transition angular frequency.",(lit,)),
            ParameterSpec("temperature_kelvin","T","K","T >= 0","Reservoir temperature.",(lit,deriv)),
            ParameterSpec("interaction_time","t","s","t >= 0","Elapsed reduced-dynamics time.",(deriv,)),
        ),
        initial_agent_state=MathematicalField(FieldStatus.VALUE,"thermal photon state with nbar=[exp(hbar omega_0/k_B T)-1]^-1",(lit,deriv)),
        assumptions=("Markovian weak coupling","thermal stationary photon reservoir","two-level system","rotating-wave exchange"),
        dynamic_regime=DynamicRegime.INCOHERENT_CPTP,
        memory_regime=MemoryRegime.MARKOVIAN,
        temporal_description="gamma_down=gamma(nbar+1), gamma_up=gamma nbar; exact generalized-amplitude-damping semigroup",
        master_equation=MathematicalField(FieldStatus.VALUE,"d rho/dt=gamma(nbar+1)D[sigma_-]rho + gamma nbar D[sigma_+]rho",(lit,deriv)),
        effective_dynamics=MathematicalField(FieldStatus.VALUE,"generalized amplitude damping with lambda=1-exp[-gamma(2nbar+1)t]",(deriv,)),
        observables=("X","Y","Z"),
        information_metrics=("von_neumann_entropy","purity","l1_coherence","fidelity","trace_distance","bloch_vector","thermal_occupation","choi_rank"),
        reversibility_class="parameter_and_time_dependent_thermal_relaxation",
        validity_domain=("single two-level system","Markovian weak-coupling thermal reservoir"),
        references=(lit,deriv),
        derivation_method="thermal Lindblad master equation solved as generalized amplitude damping",
        validation_method=("verify Kraus completeness","verify T=0 reduces to amplitude damping","verify thermal fixed point population","verify CPTP outputs"),
        maturity_level=ModelMaturityLevel.LEVEL_3,
    )


def single_mode_mechanical_phonon_model() -> CausalAgentModelRecord:
    lit=_landi()
    deriv=_author("One-mode specialization of the longitudinal bosonic dephasing model, with the bosonic coordinate interpreted as a quantized mechanical/phonon-like vibration. No hardware-specific strain transduction is assumed.")
    return CausalAgentModelRecord(
        agent_id="single-mode-mechanical-phonon-dephasing",
        provisional_name="Single-mode mechanical/phonon longitudinal coupling",
        physical_category="mechanical_vibration_phonon",
        physical_description="A quantized vibrational mode couples longitudinally to the qubit and modulates phase while preserving computational-basis populations; finite single-mode dynamics exhibits exact recurrences.",
        target_system="single qubit",
        relevant_degrees_of_freedom=("qubit","single harmonic mechanical/phonon mode"),
        coupling_mechanism="longitudinal displacement coupling sigma_z(b+b^dagger)",
        agent_hamiltonian=MathematicalField(FieldStatus.VALUE,"H_A=hbar omega_m b^dagger b",(lit,deriv)),
        interaction_hamiltonian=MathematicalField(FieldStatus.VALUE,"H_int=hbar g_m sigma_z(b+b^dagger)",(lit,deriv)),
        parameters=(
            ParameterSpec("mode_angular_frequency","omega_m","rad s^-1","omega_m > 0","Mechanical/phonon mode angular frequency.",(lit,deriv)),
            ParameterSpec("coupling_rate","g_m","rad s^-1","g_m >= 0","Effective longitudinal mode-qubit coupling.",(lit,deriv)),
            ParameterSpec("thermal_occupation","nbar","1","nbar >= 0","Mean occupation of the vibrational mode.",(lit,deriv)),
            ParameterSpec("interaction_time","t","s","t >= 0","Interaction time.",(deriv,)),
        ),
        initial_agent_state=MathematicalField(FieldStatus.VALUE,"thermal oscillator state characterized by mean occupation nbar",(lit,deriv)),
        assumptions=("single harmonic mode","longitudinal pure-dephasing coupling","initial product state","undamped oscillator during the modeled interval"),
        dynamic_regime=DynamicRegime.INCOHERENT_CPTP,
        memory_regime=MemoryRegime.NON_MARKOVIAN,
        temporal_description="rho_01(t)=q(t)rho_01(0), q=exp[-4(g_m/omega_m)^2(1-cos omega_m t)(2 nbar+1)]",
        effective_dynamics=MathematicalField(FieldStatus.VALUE,"single-mode dephasing map with exact recurrence q(2*pi/omega_m)=1",(lit,deriv)),
        observables=("X","Y","Z"),
        information_metrics=("von_neumann_entropy","purity","l1_coherence","fidelity","trace_distance","bloch_vector","coherence_factor","choi_rank"),
        reversibility_class="parameter_and_time_dependent_reduced_dephasing",
        validity_domain=("single qubit","single undamped harmonic vibrational mode","longitudinal coupling"),
        references=(lit,deriv),
        derivation_method="one-mode specialization of exact longitudinal bosonic dephasing solution",
        validation_method=("verify q(0)=1","verify q(2*pi/omega_m)=1","verify populations invariant","verify Kraus completeness and CPTP state"),
        maturity_level=ModelMaturityLevel.LEVEL_3,
        notes=("This is a generic mechanical/phonon-mode model. It does not claim a calibrated displacement amplitude or quality factor for a particular device.",),
    )


def build_physical_v2_registry() -> CausalAgentRegistry:
    registry=CausalAgentRegistry()
    base=build_final_registry()
    for agent_id in base.list_ids():
        registry.add(base.get(agent_id))
    registry.add(external_electromagnetic_drive_model())
    registry.add(external_magnetic_zeeman_model())
    registry.add(thermal_photon_reservoir_model())
    registry.add(single_mode_mechanical_phonon_model())
    return registry
