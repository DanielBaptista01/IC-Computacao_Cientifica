"""Canonical scientific schema for the Causal-Agent corpus.

This module distinguishes a physical causal model from a simulated sample.
Channel names are metadata about effective dynamics, not causal identities.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


NOT_APPLICABLE = "not_applicable"
UNRESOLVED = "unresolved"


class FieldStatus(str, Enum):
    VALUE = "value"
    NOT_APPLICABLE = NOT_APPLICABLE
    UNRESOLVED = UNRESOLVED


class ProvenanceKind(str, Enum):
    LITERATURE_DERIVED = "LITERATURE_DERIVED"
    AUTHOR_DERIVED = "AUTHOR_DERIVED"
    NUMERICALLY_DERIVED = "NUMERICALLY_DERIVED"
    PHENOMENOLOGICAL = "PHENOMENOLOGICAL"
    HYPOTHETICAL = "HYPOTHETICAL"


class ModelMaturityLevel(str, Enum):
    LEVEL_0 = "LEVEL_0"
    LEVEL_1 = "LEVEL_1"
    LEVEL_2 = "LEVEL_2"
    LEVEL_3 = "LEVEL_3"
    LEVEL_4 = "LEVEL_4"
    LEVEL_5 = "LEVEL_5"


class DynamicRegime(str, Enum):
    COHERENT_UNITARY = "coherent_unitary"
    INCOHERENT_CPTP = "incoherent_cptp"
    GENERAL_OPEN_SYSTEM = "general_open_system"


class MemoryRegime(str, Enum):
    MARKOVIAN = "markovian"
    NON_MARKOVIAN = "non_markovian"
    MIXED_OR_CROSSOVER = "mixed_or_crossover"
    UNRESOLVED = UNRESOLVED


@dataclass(frozen=True, slots=True)
class ProvenanceRecord:
    kind: ProvenanceKind
    publication: str | None = None
    authors: tuple[str, ...] = ()
    year: int | None = None
    locator: str | None = None
    assumptions: tuple[str, ...] = ()
    ic_interpretation: str | None = None
    note: str | None = None


@dataclass(frozen=True, slots=True)
class MathematicalField:
    """A mathematical object whose availability and provenance are explicit."""

    status: FieldStatus
    expression: str | None = None
    provenance: tuple[ProvenanceRecord, ...] = ()


@dataclass(frozen=True, slots=True)
class ParameterSpec:
    name: str
    symbol: str
    unit: str
    physical_range: str
    description: str
    provenance: tuple[ProvenanceRecord, ...]


@dataclass(frozen=True, slots=True)
class ProbeStateSpec:
    probe_id: str
    ket_expression: str
    bloch_vector: tuple[float, float, float]


STANDARD_PROBE_STATES: tuple[ProbeStateSpec, ...] = (
    ProbeStateSpec("0", "|0>", (0.0, 0.0, 1.0)),
    ProbeStateSpec("1", "|1>", (0.0, 0.0, -1.0)),
    ProbeStateSpec("+", "(|0>+|1>)/sqrt(2)", (1.0, 0.0, 0.0)),
    ProbeStateSpec("-", "(|0>-|1>)/sqrt(2)", (-1.0, 0.0, 0.0)),
    ProbeStateSpec("+i", "(|0>+i|1>)/sqrt(2)", (0.0, 1.0, 0.0)),
    ProbeStateSpec("-i", "(|0>-i|1>)/sqrt(2)", (0.0, -1.0, 0.0)),
)


@dataclass(slots=True)
class CausalSignature:
    """Observable/inferable signature. It is not assumed to identify a source uniquely."""

    physical_parameters: dict[str, Any] = field(default_factory=dict)
    channel_descriptors: dict[str, Any] = field(default_factory=dict)
    temporal_response: dict[str, Any] = field(default_factory=dict)
    informational_metrics: dict[str, Any] = field(default_factory=dict)
    observables: dict[str, Any] = field(default_factory=dict)
    spectrum: list[float] = field(default_factory=list)
    choi_descriptors: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


def _unresolved_math() -> MathematicalField:
    return MathematicalField(status=FieldStatus.UNRESOLVED)


@dataclass(slots=True)
class CausalAgentModelRecord:
    """One physical/mathematical causal-agent family A_k(theta)."""

    agent_id: str
    provisional_name: str
    physical_category: str
    physical_description: str
    target_system: str

    relevant_degrees_of_freedom: tuple[str, ...] = ()
    coupling_mechanism: str = UNRESOLVED
    system_hamiltonian: MathematicalField = field(default_factory=_unresolved_math)
    agent_hamiltonian: MathematicalField = field(default_factory=_unresolved_math)
    interaction_hamiltonian: MathematicalField = field(default_factory=_unresolved_math)
    parameters: tuple[ParameterSpec, ...] = ()
    initial_agent_state: MathematicalField = field(default_factory=_unresolved_math)
    assumptions: tuple[str, ...] = ()
    dynamic_regime: DynamicRegime = DynamicRegime.GENERAL_OPEN_SYSTEM
    memory_regime: MemoryRegime = MemoryRegime.UNRESOLVED
    temporal_description: str = UNRESOLVED
    master_equation: MathematicalField = field(default_factory=_unresolved_math)
    kraus_operators: MathematicalField = field(default_factory=_unresolved_math)
    superoperator: MathematicalField = field(default_factory=_unresolved_math)
    choi_matrix: MathematicalField = field(default_factory=_unresolved_math)
    unitary_transform: MathematicalField = field(default_factory=_unresolved_math)
    effective_dynamics: MathematicalField = field(default_factory=_unresolved_math)
    observables: tuple[str, ...] = ()
    information_metrics: tuple[str, ...] = ()
    reversibility_class: str = UNRESOLVED
    validity_domain: tuple[str, ...] = ()
    references: tuple[ProvenanceRecord, ...] = ()
    derivation_method: str = UNRESOLVED
    validation_method: tuple[str, ...] = ()
    maturity_level: ModelMaturityLevel = ModelMaturityLevel.LEVEL_0
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


@dataclass(slots=True)
class CausalAgentSampleRecord:
    """One parametrized sample A_k(theta_i, t_j, rho_m), not a new causal model."""

    sample_id: str
    agent_model_id: str
    parameter_values: dict[str, Any]
    time: float | None
    initial_system_state: str
    signature: CausalSignature
    random_seed: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def observable_feature_payload(self) -> dict[str, Any]:
        """Return features without textual causal labels/IDs to reduce information leakage."""
        return {
            "parameter_values": _jsonable(self.parameter_values),
            "time": self.time,
            "initial_system_state": self.initial_system_state,
            "signature": _jsonable(asdict(self.signature)),
        }

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value
