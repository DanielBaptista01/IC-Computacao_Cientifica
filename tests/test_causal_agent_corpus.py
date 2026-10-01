import numpy as np
import pytest

from ic_quantum.channels.dephasing import dephasing_kraus
from ic_quantum.data.causal_agent_schema import (
    CausalAgentModelRecord,
    CausalAgentSampleRecord,
    CausalSignature,
    DynamicRegime,
    FieldStatus,
    MathematicalField,
    MemoryRegime,
    ModelMaturityLevel,
    ParameterSpec,
    ProvenanceKind,
    ProvenanceRecord,
    STANDARD_PROBE_STATES,
)
from ic_quantum.data.provenance import validate_mathematical_field
from ic_quantum.data.registry import CausalAgentRegistry
from ic_quantum.data.validator import (
    CorpusValidationError,
    validate_density_payload,
    validate_hermitian_payload,
    validate_kraus_payload,
    validate_model_record,
    validate_sample_record,
    validate_unitary_payload,
)


def literature_ref() -> ProvenanceRecord:
    return ProvenanceRecord(
        kind=ProvenanceKind.LITERATURE_DERIVED,
        publication="Reference work",
        authors=("A. Author",),
        year=2026,
        locator="Sec. II",
        assumptions=("Finite-dimensional model",),
        ic_interpretation="Used as a controlled corpus baseline.",
    )


def valid_model() -> CausalAgentModelRecord:
    ref = literature_ref()
    return CausalAgentModelRecord(
        agent_id="controlled-z-shift",
        provisional_name="Controlled coherent Z frequency shift",
        physical_category="coherent_control_baseline",
        physical_description="Controlled Hamiltonian perturbation used as a reversible baseline.",
        target_system="single qubit",
        relevant_degrees_of_freedom=("qubit",),
        coupling_mechanism="effective longitudinal coherent perturbation",
        interaction_hamiltonian=MathematicalField(
            status=FieldStatus.VALUE,
            expression="H_int = (hbar * delta_omega / 2) sigma_z",
            provenance=(ref,),
        ),
        parameters=(
            ParameterSpec(
                name="delta_omega",
                symbol="delta_omega",
                unit="rad s^-1",
                physical_range="real; experiment-specific bounded interval",
                description="Angular-frequency offset.",
                provenance=(ref,),
            ),
        ),
        assumptions=("time-independent Hamiltonian over the interaction window",),
        dynamic_regime=DynamicRegime.COHERENT_UNITARY,
        memory_regime=MemoryRegime.MARKOVIAN,
        unitary_transform=MathematicalField(
            status=FieldStatus.VALUE,
            expression="U(t) = exp(-i H_int t / hbar)",
            provenance=(ref,),
        ),
        effective_dynamics=MathematicalField(
            status=FieldStatus.VALUE,
            expression="E_t(rho) = U(t) rho U(t)^dagger",
            provenance=(ref,),
        ),
        observables=("X", "Y", "Z"),
        information_metrics=("entropy_von_neumann", "purity", "fidelity"),
        reversibility_class="direct_unitary_inverse",
        validity_domain=("closed/effectively coherent single-qubit regime",),
        references=(ref,),
        derivation_method="unitary evolution from a time-independent Hamiltonian",
        validation_method=("compare U^dagger U with I", "recover probe states with U^dagger"),
        maturity_level=ModelMaturityLevel.LEVEL_3,
    )


def test_standard_probe_states_include_all_three_bloch_axes():
    assert {probe.probe_id for probe in STANDARD_PROBE_STATES} == {
        "0", "1", "+", "-", "+i", "-i"
    }
    assert {probe.bloch_vector for probe in STANDARD_PROBE_STATES} == {
        (0.0, 0.0, 1.0),
        (0.0, 0.0, -1.0),
        (1.0, 0.0, 0.0),
        (-1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, -1.0, 0.0),
    }


def test_unresolved_and_not_applicable_are_not_silently_equated_with_values():
    unresolved = MathematicalField(status=FieldStatus.UNRESOLVED)
    not_applicable = MathematicalField(status=FieldStatus.NOT_APPLICABLE)
    assert validate_mathematical_field(unresolved, "field") == []
    assert validate_mathematical_field(not_applicable, "field") == []

    invalid = MathematicalField(
        status=FieldStatus.UNRESOLVED,
        expression="silently supplied expression",
    )
    assert validate_mathematical_field(invalid, "field")


def test_literature_derived_equation_requires_scientific_locator():
    ref = ProvenanceRecord(
        kind=ProvenanceKind.LITERATURE_DERIVED,
        publication="Reference work",
        authors=("A. Author",),
        year=2026,
        ic_interpretation="Used in the IC.",
    )
    field = MathematicalField(
        status=FieldStatus.VALUE,
        expression="H = H^dagger",
        provenance=(ref,),
    )
    assert any("locator" in error for error in validate_mathematical_field(field, "H"))


def test_valid_model_passes_and_registry_rejects_duplicate_identity():
    model = valid_model()
    validate_model_record(model)
    registry = CausalAgentRegistry()
    registry.add(model)
    assert registry.list_ids() == ("controlled-z-shift",)
    with pytest.raises(CorpusValidationError):
        registry.add(model)


def test_sample_is_an_instantiation_and_observable_payload_excludes_causal_labels():
    model = valid_model()
    sample = CausalAgentSampleRecord(
        sample_id="controlled-z-shift__dw1__t070",
        agent_model_id=model.agent_id,
        parameter_values={"delta_omega": 1.0},
        time=0.7,
        initial_system_state="+i",
        signature=CausalSignature(
            observables={"X": 0.1, "Y": 0.9, "Z": 0.0},
            informational_metrics={"purity": 1.0},
        ),
        metadata={"source_name": "must_remain_metadata_only"},
    )
    validate_sample_record(sample, model)
    payload = sample.observable_feature_payload()
    assert "agent_model_id" not in payload
    assert "sample_id" not in payload
    assert "metadata" not in payload


def test_sample_requires_all_model_parameters():
    model = valid_model()
    sample = CausalAgentSampleRecord(
        sample_id="bad",
        agent_model_id=model.agent_id,
        parameter_values={},
        time=0.1,
        initial_system_state="0",
        signature=CausalSignature(),
    )
    with pytest.raises(CorpusValidationError):
        validate_sample_record(sample, model)


def test_numerical_validation_gate_accepts_physical_payloads():
    sigma_z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
    validate_hermitian_payload(sigma_z)
    validate_unitary_payload(np.eye(2, dtype=complex))
    validate_kraus_payload(dephasing_kraus(0.2))
    validate_density_payload(np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex))


def test_numerical_validation_gate_rejects_invalid_kraus_set():
    with pytest.raises(CorpusValidationError):
        validate_kraus_payload([np.eye(2, dtype=complex), np.eye(2, dtype=complex)])
