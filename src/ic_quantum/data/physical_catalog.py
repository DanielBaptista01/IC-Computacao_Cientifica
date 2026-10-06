"""Validated catalog for the physical-source expansion (v2).

This catalog does not replace the frozen mechanistic baseline.  It contains only
families whose physical source is explicit enough to support the chain

physical source -> coupling mechanism -> mathematical dynamics -> signature.

The ionizing-radiation entry is deliberately phenomenological at the reduced
quasiparticle-kinetics level: no microscopic radiation Hamiltonian is invented.
"""

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
from ic_quantum.data.final_catalog import (
    finite_mode_spin_boson_dephasing_model,
    markovian_photon_reservoir_decay_model,
)
from ic_quantum.data.registry import CausalAgentRegistry


def _author(note: str) -> ProvenanceRecord:
    return ProvenanceRecord(kind=ProvenanceKind.AUTHOR_DERIVED, note=note)


def _phenomenological(note: str) -> ProvenanceRecord:
    return ProvenanceRecord(kind=ProvenanceKind.PHENOMENOLOGICAL, note=note)


def _altafini_ticozzi() -> ProvenanceRecord:
    return ProvenanceRecord(
        kind=ProvenanceKind.LITERATURE_DERIVED,
        publication="Modeling and Control of Quantum Systems: An Introduction (arXiv:1210.7127)",
        authors=("Claudio Altafini", "Francesco Ticozzi"),
        year=2012,
        locator=(
            "Sec. III: Hamiltonian control; Sec. IV.E: field action as a semiclassical "
            "Hamiltonian perturbation; controlled two-level examples with magnetic fields"
        ),
        assumptions=(
            "finite-dimensional effective quantum system",
            "semiclassical external-field description for the coherent regime",
        ),
        ic_interpretation=(
            "Used to model an external magnetic component of an electromagnetic field "
            "as a time-dependent Hamiltonian perturbation of a spin-1/2 qubit."
        ),
    )


def _charge_noise_reference() -> ProvenanceRecord:
    return ProvenanceRecord(
        kind=ProvenanceKind.LITERATURE_DERIVED,
        publication="Dephasing due to background charge fluctuations, Phys. Rev. B 67, 195320",
        authors=("Toshifumi Itakura", "Yasuhiro Tokura"),
        year=2003,
        locator="Random-telegraph background-charge model and qubit dephasing analysis",
        assumptions=(
            "bistable charge fluctuation",
            "effective two-level qubit",
            "ensemble-averaged dephasing description",
        ),
        ic_interpretation=(
            "Used to represent a localized bistable charge/defect source rather than "
            "using 'dephasing' as the causal identity."
        ),
    )


def _mechanical_reference() -> ProvenanceRecord:
    return ProvenanceRecord(
        kind=ProvenanceKind.LITERATURE_DERIVED,
        publication="Circuit quantum acoustodynamics with surface acoustic waves, Nat. Commun. 8, 975",
        authors=(
            "Riccardo Manenti",
            "Anton F. Kockum",
            "Andrew Patterson",
            "Tanja Behrle",
            "Joseph Rahamim",
            "Giovanna Tancredi",
            "Franco Nori",
            "Peter J. Leek",
        ),
        year=2017,
        locator=(
            "Interaction between a SAW cavity and a superconducting qubit: "
            "generalized Jaynes-Cummings coupling to the acoustic mode"
        ),
        assumptions=(
            "two-level qubit truncation in the implemented IC model",
            "single selected mechanical/acoustic mode",
            "rotating-wave excitation-exchange interaction",
            "finite Fock-space truncation is a numerical approximation of the IC",
        ),
        ic_interpretation=(
            "Used as a physically explicit mechanical/phononic source.  The IC keeps "
            "one acoustic mode and traces it out to obtain the qubit reduced channel."
        ),
    )


def _vepsalainen_radiation() -> ProvenanceRecord:
    return ProvenanceRecord(
        kind=ProvenanceKind.LITERATURE_DERIVED,
        publication="Impact of ionizing radiation on superconducting qubit coherence, Nature 584, 551-556",
        authors=(
            "Antti P. Vepsalainen",
            "Amir H. Karamlou",
            "John L. Orrell",
            "Akshunna S. Dogra",
            "Ben Loer",
            "Francisca Vasconcelos",
            "Simon Gustavsson",
            "Joseph A. Formaggio",
            "Brent A. VanDevender",
            "William D. Oliver",
        ),
        year=2020,
        locator="Ionizing-radiation exposure, quasiparticle generation and qubit relaxation",
        assumptions=("superconducting qubit platform", "ionizing radiation creates excess quasiparticles"),
        ic_interpretation=(
            "Supports the physical source assignment: environmental radioactivity and "
            "cosmic radiation can generate excess quasiparticles that reduce qubit T1."
        ),
    )


def _martinis_radiation() -> ProvenanceRecord:
    return ProvenanceRecord(
        kind=ProvenanceKind.LITERATURE_DERIVED,
        publication=(
            "Saving superconducting quantum processors from decay and correlated errors "
            "generated by gamma and cosmic rays, npj Quantum Information 7, 90"
        ),
        authors=("John M. Martinis",),
        year=2021,
        locator=(
            "Eqs. (1)-(3), radiation -> phonon/quasiparticle down-conversion and "
            "quasiparticle-limited qubit quality factor"
        ),
        assumptions=("aluminum superconducting-qubit context", "post-impact quasiparticle description"),
        ic_interpretation=(
            "Provides the physical chain from ionizing energy deposition to phonons, "
            "quasiparticles and enhanced relaxation.  The IC does not claim to simulate "
            "the complete spatial cascade."
        ),
    )


def _wang_quasiparticle_kinetics() -> ProvenanceRecord:
    return ProvenanceRecord(
        kind=ProvenanceKind.LITERATURE_DERIVED,
        publication="Measurement and control of quasiparticle dynamics in a superconducting qubit, Nat. Commun. 5, 5836",
        authors=(
            "C. Wang",
            "Y. Y. Gao",
            "I. M. Pop",
            "U. Vool",
            "C. Axline",
            "T. Brecht",
            "R. W. Heeres",
            "L. Frunzio",
            "M. H. Devoret",
            "G. Catelani",
            "L. I. Glazman",
            "R. J. Schoelkopf",
        ),
        year=2014,
        locator=(
            "Quasiparticle kinetics dx_qp/dt = -r x_qp^2 - s x_qp + g and "
            "qubit relaxation Gamma(t)=C x_qp(t)+Gamma_ex"
        ),
        assumptions=("superconducting transmon/quasiparticle phenomenology",),
        ic_interpretation=(
            "Used for post-impact quasiparticle relaxation kinetics after the physical "
            "ionizing-radiation source has generated excess quasiparticles."
        ),
    )


def external_magnetic_field_model() -> CausalAgentModelRecord:
    literature = _altafini_ticozzi()
    derived = _author(
        "For a fixed field orientation, H(t) commutes at different times; integrating "
        "gamma B0 cos(omega t+phi) gives an exact spin-1/2 rotation.  A zero-mean "
        "quasistatic Gaussian longitudinal-field ensemble gives "
        "W(t)=exp[-(gamma sigma_B t)^2/2]."
    )
    return CausalAgentModelRecord(
        agent_id="external-magnetic-field-wave",
        provisional_name="External magnetic component of an electromagnetic field",
        physical_category="external_electromagnetic_magnetic_field",
        physical_description=(
            "A coherent or slowly fluctuating external magnetic field couples to the "
            "magnetic moment of an effective spin-1/2 qubit.  The deterministic regime "
            "produces coherent rotations; an ensemble of quasistatic longitudinal "
            "field offsets produces dephasing."
        ),
        target_system="effective spin-1/2 qubit",
        physical_source="external electromagnetic field (magnetic component)",
        causal_mechanism="Zeeman coupling of the qubit magnetic moment to B(t)",
        relevant_degrees_of_freedom=("qubit spin", "classical external magnetic field"),
        interaction_hamiltonian=MathematicalField(
            status=FieldStatus.VALUE,
            expression=(
                "H_int(t)/hbar = [gamma B0 cos(omega_d t + phi)/2] n.sigma; "
                "quasistatic fluctuation: delta_omega=gamma delta_B"
            ),
            provenance=(literature, derived),
        ),
        parameters=(
            ParameterSpec(
                "gyromagnetic_ratio", "gamma", "rad s^-1 T^-1", "gamma > 0",
                "Effective spin gyromagnetic ratio.", (literature,)
            ),
            ParameterSpec(
                "field_amplitude", "B0", "T", "B0 >= 0",
                "Coherent magnetic-field amplitude.", (literature,)
            ),
            ParameterSpec(
                "field_standard_deviation", "sigma_B", "T", "sigma_B >= 0",
                "RMS quasistatic longitudinal field fluctuation.", (derived,)
            ),
            ParameterSpec(
                "drive_angular_frequency", "omega_d", "rad s^-1", "omega_d >= 0",
                "Angular frequency of the coherent field.", (literature,)
            ),
            ParameterSpec(
                "phase", "phi", "rad", "real",
                "Initial phase of the coherent field.", (derived,)
            ),
            ParameterSpec(
                "polar_angle", "theta", "rad", "0 <= theta <= pi",
                "Field orientation polar angle.", (derived,)
            ),
            ParameterSpec(
                "azimuth_angle", "varphi", "rad", "real modulo 2*pi",
                "Field orientation azimuth.", (derived,)
            ),
            ParameterSpec(
                "interaction_time", "t", "s", "t >= 0",
                "Exposure duration.", (literature,)
            ),
        ),
        assumptions=(
            "spin-1/2 effective description",
            "fixed field orientation in each coherent sample",
            "Gaussian regime is an ensemble average of quasistatic longitudinal offsets",
            "electric-dipole coupling is not represented by this family",
        ),
        dynamic_regime=DynamicRegime.GENERAL_OPEN_SYSTEM,
        memory_regime=MemoryRegime.MIXED_OR_CROSSOVER,
        temporal_description=(
            "Coherent: exact time-integrated Zeeman rotation.  Quasistatic ensemble: "
            "rho_01(t)=exp[-(gamma sigma_B t)^2/2] rho_01(0)."
        ),
        unitary_transform=MathematicalField(
            status=FieldStatus.VALUE,
            expression="U(t)=exp[-i Theta(t) n.sigma/2]",
            provenance=(derived, literature),
        ),
        kraus_operators=MathematicalField(
            status=FieldStatus.VALUE,
            expression="K0=sqrt((1+W)/2)I; K1=sqrt((1-W)/2)sigma_z",
            provenance=(derived,),
        ),
        effective_dynamics=MathematicalField(
            status=FieldStatus.VALUE,
            expression="condition-dependent coherent rotation or Gaussian ensemble dephasing",
            provenance=(derived, literature),
        ),
        observables=("X", "Y", "Z"),
        information_metrics=(
            "von_neumann_entropy", "purity", "l1_coherence", "fidelity",
            "trace_distance", "bloch_vector", "choi_rank"
        ),
        reversibility_class="condition_dependent_unitary_or_ensemble_dephasing",
        validity_domain=(
            "effective spin-1/2 qubit",
            "semiclassical magnetic field",
            "fixed-axis coherent drive or quasistatic Gaussian longitudinal fluctuations",
        ),
        references=(literature, derived),
        derivation_method=(
            "Zeeman Hamiltonian integration for fixed orientation; characteristic "
            "function of a Gaussian frequency-offset ensemble for dephasing"
        ),
        validation_method=(
            "zero-field and zero-time identity limits",
            "analytic DC rotation comparison",
            "unitarity for coherent regime",
            "Kraus completeness and CPTP validation for Gaussian ensemble regime",
            "entropy preservation for coherent regime",
        ),
        maturity_level=ModelMaturityLevel.LEVEL_3,
    )


def mechanical_phonon_mode_model() -> CausalAgentModelRecord:
    literature = _mechanical_reference()
    derived = _author(
        "The IC truncates the mechanical Fock space, initializes it thermally, evolves "
        "the qubit+mode jointly, and derives Kraus operators from the same unitary and "
        "thermal state for an independent reduced-map validation."
    )
    return CausalAgentModelRecord(
        agent_id="mechanical-phonon-mode",
        provisional_name="Mechanical/acoustic phonon mode coupled to a qubit",
        physical_category="mechanical_vibration_phonon_exchange",
        physical_description=(
            "A quantized acoustic/mechanical mode exchanges excitations with a two-level "
            "qubit through a Jaynes-Cummings-type interaction.  The mode may be thermally "
            "populated, so tracing it out can produce relaxation and excitation."
        ),
        target_system="two-level qubit coupled to a mechanical/acoustic resonator",
        physical_source="mechanical vibration / acoustic phonon mode",
        causal_mechanism="resonant qubit-phonon excitation exchange",
        relevant_degrees_of_freedom=("qubit", "single quantized mechanical mode"),
        system_hamiltonian=MathematicalField(
            status=FieldStatus.VALUE,
            expression="H_S/hbar = omega_q |1><1|",
            provenance=(literature,),
        ),
        agent_hamiltonian=MathematicalField(
            status=FieldStatus.VALUE,
            expression="H_A/hbar = omega_m b^dagger b",
            provenance=(literature,),
        ),
        interaction_hamiltonian=MathematicalField(
            status=FieldStatus.VALUE,
            expression="H_int/hbar = g (sigma_+ b + sigma_- b^dagger)",
            provenance=(literature,),
        ),
        parameters=(
            ParameterSpec(
                "mode_angular_frequency", "omega_m", "rad s^-1", "omega_m > 0",
                "Mechanical/acoustic mode angular frequency.", (literature,)
            ),
            ParameterSpec(
                "coupling_rate", "g", "rad s^-1", "g >= 0",
                "Qubit-phonon excitation-exchange coupling.", (literature,)
            ),
            ParameterSpec(
                "temperature_kelvin", "T", "K", "T >= 0",
                "Temperature used to initialize the oscillator thermal state.", (derived,)
            ),
            ParameterSpec(
                "interaction_time", "t", "s", "t >= 0",
                "Interaction duration.", (literature,)
            ),
        ),
        initial_agent_state=MathematicalField(
            status=FieldStatus.VALUE,
            expression="rho_A proportional to exp[-hbar omega_m b^dagger b/(k_B T)]",
            provenance=(derived, literature),
        ),
        assumptions=(
            "single selected acoustic mode",
            "two-level qubit",
            "rotating-wave excitation-exchange coupling",
            "resonant default omega_q=omega_m in the dataset",
            "finite Fock-space truncation with convergence checked by retained thermal weight",
        ),
        dynamic_regime=DynamicRegime.INCOHERENT_CPTP,
        memory_regime=MemoryRegime.MIXED_OR_CROSSOVER,
        temporal_description=(
            "rho_S(t)=Tr_m[U(t)(rho_S tensor rho_m,T)U^dagger(t)] with finite-mode recurrences"
        ),
        kraus_operators=MathematicalField(
            status=FieldStatus.VALUE,
            expression="K_mn=sqrt(p_n)<m|U|n> for thermal p_n",
            provenance=(derived,),
        ),
        unitary_transform=MathematicalField(
            status=FieldStatus.VALUE,
            expression="U(t)=exp[-i(H_S+H_A+H_int)t/hbar]",
            provenance=(derived, literature),
        ),
        effective_dynamics=MathematicalField(
            status=FieldStatus.VALUE,
            expression="E_t(rho)=Tr_m[U(t)(rho tensor rho_m,T)U^dagger(t)]",
            provenance=(derived, literature),
        ),
        observables=("X", "Y", "Z"),
        information_metrics=(
            "von_neumann_entropy", "purity", "l1_coherence", "fidelity",
            "trace_distance", "bloch_vector", "choi_rank"
        ),
        reversibility_class="reduced_qubit_map_depends_on_g_T_and_time",
        validity_domain=(
            "one qubit plus one selected quantized mechanical mode",
            "finite thermal Fock truncation",
            "Jaynes-Cummings/RWA interaction",
        ),
        references=(literature, derived),
        derivation_method="explicit global unitary plus partial trace and equivalent thermal Kraus construction",
        validation_method=(
            "Hamiltonian Hermiticity and global unitarity",
            "thermal state positivity/normalization",
            "Kraus completeness",
            "Kraus evolution equals explicit partial trace",
            "zero-coupling and zero-time limits",
        ),
        maturity_level=ModelMaturityLevel.LEVEL_3,
    )


def ionizing_radiation_quasiparticle_model() -> CausalAgentModelRecord:
    source = _vepsalainen_radiation()
    cascade = _martinis_radiation()
    kinetics = _wang_quasiparticle_kinetics()
    reduced = _phenomenological(
        "The IC starts the numerical sample after the radiation event has produced an "
        "initial excess quasiparticle fraction x_qp(0).  It evolves x_qp with the "
        "literature recombination/trapping equation and maps Gamma_1(t) to a time-dependent "
        "amplitude-damping survival probability.  Energy-deposition-to-x_qp conversion "
        "and spatial multi-qubit propagation are not claimed to be simulated."
    )
    return CausalAgentModelRecord(
        agent_id="ionizing-radiation-quasiparticle-burst",
        provisional_name="Ionizing-radiation-induced quasiparticle relaxation burst",
        physical_category="ionizing_radiation_quasiparticle_burst",
        physical_description=(
            "A cosmic-ray muon or environmental gamma event deposits energy in a "
            "superconducting device, producing high-energy phonons and excess "
            "quasiparticles.  The implemented reduced model begins at the post-impact "
            "quasiparticle fraction and quantifies its effect on qubit relaxation."
        ),
        target_system="superconducting qubit/transmon reduced to two levels",
        physical_source="ionizing radiation: cosmic-ray muon or environmental gamma event",
        causal_mechanism=(
            "energy deposition -> phonon down-conversion -> Cooper-pair breaking -> "
            "quasiparticle population -> enhanced qubit energy relaxation"
        ),
        relevant_degrees_of_freedom=(
            "superconducting qubit",
            "nonequilibrium quasiparticle population",
            "phonon cascade represented only through initial quasiparticle condition",
        ),
        interaction_hamiltonian=MathematicalField(
            status=FieldStatus.NOT_APPLICABLE,
            provenance=(reduced,),
        ),
        parameters=(
            ParameterSpec(
                "initial_quasiparticle_fraction", "x_qp0", "1", "x_qp0 >= 0",
                "Post-impact quasiparticle density normalized by Cooper-pair density.",
                (cascade, kinetics)
            ),
            ParameterSpec(
                "recombination_rate", "r", "s^-1", "r >= 0",
                "Coefficient of the pair-recombination term r*x_qp^2.", (kinetics,)
            ),
            ParameterSpec(
                "trapping_rate", "s", "s^-1", "s >= 0",
                "Single-quasiparticle trapping/removal rate.", (kinetics,)
            ),
            ParameterSpec(
                "generation_rate", "g_qp", "s^-1", "g_qp >= 0",
                "Background normalized quasiparticle generation rate.", (kinetics,)
            ),
            ParameterSpec(
                "qp_relaxation_coefficient", "C", "s^-1", "C >= 0",
                "Proportionality Gamma_qp=C*x_qp in the reduced relaxation model.",
                (kinetics, cascade)
            ),
            ParameterSpec(
                "background_relaxation_rate", "Gamma_ex", "s^-1", "Gamma_ex >= 0",
                "Non-quasiparticle background relaxation rate.", (kinetics,)
            ),
            ParameterSpec(
                "interaction_time", "t", "s", "t >= 0",
                "Elapsed time after the ionizing event.", (source, kinetics)
            ),
        ),
        assumptions=(
            "superconducting-qubit platform",
            "event-conditioned model: no stochastic arrival-time process is sampled",
            "spatial propagation and correlated multi-qubit errors are outside this one-qubit implementation",
            "initial quasiparticle fraction summarizes the unresolved deposition/down-conversion geometry",
        ),
        dynamic_regime=DynamicRegime.INCOHERENT_CPTP,
        memory_regime=MemoryRegime.MIXED_OR_CROSSOVER,
        temporal_description=(
            "dx_qp/dt=-r x_qp^2-s x_qp+g_qp; "
            "Gamma_1(t)=C x_qp(t)+Gamma_ex; "
            "eta(t)=exp[-integral Gamma_1(s) ds]"
        ),
        master_equation=MathematicalField(
            status=FieldStatus.VALUE,
            expression=(
                "d rho/dt = Gamma_1(t)[sigma_- rho sigma_+ "
                "- 1/2{sigma_+sigma_-,rho}]"
            ),
            provenance=(reduced, kinetics),
        ),
        kraus_operators=MathematicalField(
            status=FieldStatus.VALUE,
            expression="amplitude-damping Kraus pair with p(t)=1-exp[-integral Gamma_1 ds]",
            provenance=(reduced,),
        ),
        effective_dynamics=MathematicalField(
            status=FieldStatus.VALUE,
            expression="event-conditioned time-dependent amplitude-damping reduced channel",
            provenance=(reduced, source, cascade, kinetics),
        ),
        observables=("X", "Y", "Z"),
        information_metrics=(
            "von_neumann_entropy", "purity", "l1_coherence", "fidelity",
            "trace_distance", "bloch_vector", "quasiparticle_fraction", "choi_rank"
        ),
        reversibility_class="time_dependent_nonunitary_relaxation",
        validity_domain=(
            "event-conditioned single superconducting qubit",
            "post-impact quasiparticle kinetics",
            "phenomenological reduced channel; not a microscopic radiation Hamiltonian",
        ),
        references=(source, cascade, kinetics, reduced),
        derivation_method=(
            "literature physical source chain plus literature quasiparticle kinetic equation; "
            "IC integrates the time-dependent relaxation hazard"
        ),
        validation_method=(
            "zero-time identity",
            "non-negative quasiparticle fraction and relaxation hazard",
            "analytic trapping-only limit",
            "Kraus completeness and CPTP output",
            "monotone survival probability for non-negative rates",
        ),
        maturity_level=ModelMaturityLevel.LEVEL_3,
        notes=(
            "PHENOMENOLOGICAL at the source-to-reduced-channel bridge.  The mapping from "
            "deposited particle energy/location to x_qp0 is intentionally unresolved.",
        ),
    )


def bistable_charge_fluctuator_model() -> CausalAgentModelRecord:
    literature = _charge_noise_reference()
    derived = _author(
        "For symmetric telegraph xi(t)=+-1 with transition rate nu, the conditional "
        "coherences obey a 2x2 Markov generator.  Their sum satisfies "
        "W''+2nu W'+v^2 W=0, yielding the exact ensemble coherence used in the IC."
    )
    return CausalAgentModelRecord(
        agent_id="bistable-charge-fluctuator-rtn",
        provisional_name="Bistable charge-defect random-telegraph fluctuation",
        physical_category="charge_noise_two_level_fluctuator",
        physical_description=(
            "A localized bistable charge defect switches between two configurations and "
            "modulates the qubit level splitting.  Ensemble averaging the telegraph "
            "process produces non-Gaussian dephasing whose temporal form depends on the "
            "ratio of coupling strength to switching rate."
        ),
        target_system="charge-sensitive or frequency-sensitive effective qubit",
        physical_source="localized bistable charge trap / two-level material fluctuator",
        causal_mechanism="random-telegraph modulation of the qubit energy splitting",
        relevant_degrees_of_freedom=("qubit", "classical bistable fluctuator"),
        interaction_hamiltonian=MathematicalField(
            status=FieldStatus.VALUE,
            expression="H_noise(t)/hbar = [v xi(t)/2] sigma_z, xi(t)=+-1",
            provenance=(literature, derived),
        ),
        parameters=(
            ParameterSpec(
                "coupling_rate", "v", "rad s^-1", "v >= 0",
                "Magnitude of the qubit frequency shift caused by the fluctuator.",
                (literature, derived)
            ),
            ParameterSpec(
                "switching_rate", "nu", "s^-1", "nu >= 0",
                "Transition rate out of each telegraph state.", (literature, derived)
            ),
            ParameterSpec(
                "interaction_time", "t", "s", "t >= 0",
                "Observation time.", (literature,)
            ),
        ),
        assumptions=(
            "single symmetric bistable fluctuator",
            "pure longitudinal coupling",
            "equal initial probability for the two fluctuator states",
            "ensemble-averaged reduced state; no Monte-Carlo trajectories are sampled",
        ),
        dynamic_regime=DynamicRegime.INCOHERENT_CPTP,
        memory_regime=MemoryRegime.MIXED_OR_CROSSOVER,
        temporal_description=(
            "rho_01(t)=W(t)rho_01(0), where W solves "
            "W''+2nu W'+v^2 W=0 with W(0)=1 and W'(0)=0"
        ),
        kraus_operators=MathematicalField(
            status=FieldStatus.VALUE,
            expression="K0=sqrt((1+W)/2)I; K1=sqrt((1-W)/2)sigma_z",
            provenance=(derived,),
        ),
        effective_dynamics=MathematicalField(
            status=FieldStatus.VALUE,
            expression="exact ensemble pure-dephasing map generated by symmetric RTN",
            provenance=(literature, derived),
        ),
        observables=("X", "Y", "Z"),
        information_metrics=(
            "von_neumann_entropy", "purity", "l1_coherence", "fidelity",
            "trace_distance", "bloch_vector", "RTN_spectral_density", "choi_rank"
        ),
        reversibility_class="parameter_and_time_dependent_RTN_dephasing",
        validity_domain=(
            "single bistable fluctuator",
            "pure-dephasing longitudinal coupling",
            "symmetric switching process",
        ),
        references=(literature, derived),
        derivation_method="exact solution of the conditional telegraph-noise coherence generator",
        validation_method=(
            "zero-coupling and zero-time identity limits",
            "exact comparison against the 2x2 conditional-generator matrix exponential",
            "Kraus completeness and CPTP validation",
            "strong- and weak-coupling regimes",
        ),
        maturity_level=ModelMaturityLevel.LEVEL_3,
    )


def build_physical_source_registry() -> CausalAgentRegistry:
    registry = CausalAgentRegistry()
    registry.add(external_magnetic_field_model())
    registry.add(finite_mode_spin_boson_dephasing_model())
    registry.add(markovian_photon_reservoir_decay_model())
    registry.add(mechanical_phonon_mode_model())
    registry.add(ionizing_radiation_quasiparticle_model())
    registry.add(bistable_charge_fluctuator_model())
    return registry
