"""Validation gate for records before they enter the scientific corpus."""

from __future__ import annotations

import re

import numpy as np

from ic_quantum.core.validation import (
    validate_density_matrix,
    validate_kraus,
    validate_unitary,
)
from ic_quantum.data.causal_agent_schema import (
    CausalAgentModelRecord,
    CausalAgentSampleRecord,
    FieldStatus,
    ModelMaturityLevel,
)
from ic_quantum.data.provenance import (
    validate_mathematical_field,
    validate_provenance_record,
)
from ic_quantum.dynamics.reversibility import is_cptp_superoperator


_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class CorpusValidationError(ValueError):
    pass


def model_validation_errors(model: CausalAgentModelRecord) -> list[str]:
    errors: list[str] = []

    if not _ID_RE.fullmatch(model.agent_id):
        errors.append("agent_id must be a stable lowercase slug.")
    for name, value in (
        ("provisional_name", model.provisional_name),
        ("physical_category", model.physical_category),
        ("physical_description", model.physical_description),
        ("target_system", model.target_system),
        ("physical_source", model.physical_source),
        ("causal_mechanism", model.causal_mechanism),
    ):
        if not value.strip():
            errors.append(f"{name} must be non-empty.")

    if model.maturity_level in {
        ModelMaturityLevel.LEVEL_3,
        ModelMaturityLevel.LEVEL_4,
        ModelMaturityLevel.LEVEL_5,
    }:
        if model.physical_source == "unresolved":
            errors.append("LEVEL_3+ models require an explicit physical_source.")
        if model.causal_mechanism == "unresolved":
            errors.append("LEVEL_3+ models require an explicit causal_mechanism.")

    if not model.references:
        errors.append("A causal-agent model cannot enter the corpus without provenance.")
    for index, record in enumerate(model.references):
        for error in validate_provenance_record(record):
            errors.append(f"references[{index}]: {error}")

    parameter_names: set[str] = set()
    for index, parameter in enumerate(model.parameters):
        if parameter.name in parameter_names:
            errors.append(f"Duplicate parameter name: {parameter.name}.")
        parameter_names.add(parameter.name)
        if not parameter.name or not parameter.symbol:
            errors.append(f"parameters[{index}] requires name and symbol.")
        if not parameter.unit:
            errors.append(
                f"parameters[{index}] requires an explicit unit; use '1' if dimensionless."
            )
        if not parameter.physical_range:
            errors.append(f"parameters[{index}] requires a physical range/domain.")
        if not parameter.provenance:
            errors.append(f"parameters[{index}] requires provenance.")
        for p_index, record in enumerate(parameter.provenance):
            for error in validate_provenance_record(record):
                errors.append(f"parameters[{index}].provenance[{p_index}]: {error}")

    mathematical_fields = {
        "system_hamiltonian": model.system_hamiltonian,
        "agent_hamiltonian": model.agent_hamiltonian,
        "interaction_hamiltonian": model.interaction_hamiltonian,
        "initial_agent_state": model.initial_agent_state,
        "master_equation": model.master_equation,
        "kraus_operators": model.kraus_operators,
        "superoperator": model.superoperator,
        "choi_matrix": model.choi_matrix,
        "unitary_transform": model.unitary_transform,
        "effective_dynamics": model.effective_dynamics,
    }
    for field_name, value in mathematical_fields.items():
        errors.extend(validate_mathematical_field(value, field_name))

    if model.maturity_level in {
        ModelMaturityLevel.LEVEL_3,
        ModelMaturityLevel.LEVEL_4,
        ModelMaturityLevel.LEVEL_5,
    } and not model.validation_method:
        errors.append("LEVEL_3+ models require an explicit numerical validation method.")

    if model.interaction_hamiltonian.status is FieldStatus.NOT_APPLICABLE:
        if model.master_equation.status is FieldStatus.UNRESOLVED and model.effective_dynamics.status is FieldStatus.UNRESOLVED:
            errors.append(
                "If H_int is not applicable, the effective/master-equation description "
                "must not also remain entirely unresolved."
            )

    return errors


def validate_model_record(model: CausalAgentModelRecord) -> None:
    errors = model_validation_errors(model)
    if errors:
        raise CorpusValidationError("; ".join(errors))


def sample_validation_errors(
    sample: CausalAgentSampleRecord,
    model: CausalAgentModelRecord,
) -> list[str]:
    errors: list[str] = []
    if sample.agent_model_id != model.agent_id:
        errors.append("sample.agent_model_id does not match the model.")
    required = {parameter.name for parameter in model.parameters}
    missing = sorted(required.difference(sample.parameter_values))
    if missing:
        errors.append(f"sample is missing parameter values: {missing}.")
    if not sample.sample_id.strip():
        errors.append("sample_id must be non-empty.")
    if not sample.initial_system_state.strip():
        errors.append("initial_system_state must be non-empty.")
    return errors


def validate_sample_record(
    sample: CausalAgentSampleRecord,
    model: CausalAgentModelRecord,
) -> None:
    errors = sample_validation_errors(sample, model)
    if errors:
        raise CorpusValidationError("; ".join(errors))


def validate_hermitian_payload(operator: np.ndarray, atol: float = 1e-10) -> None:
    matrix = np.asarray(operator, dtype=complex)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise CorpusValidationError("Hamiltonian/operator must be square.")
    if not np.allclose(matrix, matrix.conjugate().T, atol=atol, rtol=0.0):
        raise CorpusValidationError("Hamiltonian/operator must be Hermitian.")


def validate_unitary_payload(operator: np.ndarray, atol: float = 1e-10) -> None:
    try:
        validate_unitary(operator, atol=atol)
    except ValueError as exc:
        raise CorpusValidationError(str(exc)) from exc


def validate_kraus_payload(kraus_ops: list[np.ndarray], atol: float = 1e-10) -> None:
    try:
        validate_kraus(kraus_ops, atol=atol)
    except ValueError as exc:
        raise CorpusValidationError(str(exc)) from exc


def validate_density_payload(rho: np.ndarray, atol: float = 1e-10) -> None:
    try:
        validate_density_matrix(rho, atol=atol)
    except ValueError as exc:
        raise CorpusValidationError(str(exc)) from exc


def validate_cptp_superoperator_payload(
    superoperator: np.ndarray,
    dimension: int,
    atol: float = 1e-10,
) -> None:
    if not is_cptp_superoperator(superoperator, dimension, atol=atol):
        raise CorpusValidationError("Superoperator is not CPTP within tolerance.")
