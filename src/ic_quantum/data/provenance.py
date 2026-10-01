"""Scientific provenance rules for the Causal-Agent corpus."""

from __future__ import annotations

from ic_quantum.data.causal_agent_schema import (
    FieldStatus,
    MathematicalField,
    ProvenanceKind,
    ProvenanceRecord,
)


def validate_provenance_record(record: ProvenanceRecord) -> list[str]:
    errors: list[str] = []
    if record.kind is ProvenanceKind.LITERATURE_DERIVED:
        if not record.publication:
            errors.append("Literature-derived provenance requires publication.")
        if not record.authors:
            errors.append("Literature-derived provenance requires authors.")
        if record.year is None:
            errors.append("Literature-derived provenance requires year.")
        if not record.locator:
            errors.append("Literature-derived provenance requires equation/section locator.")
        if not record.ic_interpretation:
            errors.append("Literature-derived provenance requires the IC interpretation/adaptation.")
    return errors


def validate_mathematical_field(field: MathematicalField, field_name: str) -> list[str]:
    errors: list[str] = []
    if field.status is FieldStatus.VALUE:
        if not field.expression or not field.expression.strip():
            errors.append(f"{field_name}: status=value requires an expression.")
        if not field.provenance:
            errors.append(f"{field_name}: every mathematical expression requires provenance.")
    else:
        if field.expression is not None:
            errors.append(
                f"{field_name}: unresolved/not_applicable must not carry a mathematical expression."
            )

    for index, record in enumerate(field.provenance):
        for error in validate_provenance_record(record):
            errors.append(f"{field_name}.provenance[{index}]: {error}")
    return errors
