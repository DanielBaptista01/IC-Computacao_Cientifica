import numpy as np

from ic_quantum.data.causal_agent_schema import ModelMaturityLevel, ProvenanceKind
from ic_quantum.data.physical_catalog import build_physical_source_registry
from ic_quantum.data.validator import validate_model_record
from ic_quantum.dynamics.external_field import (
    gaussian_quasistatic_field_coherence_factor,
    gaussian_quasistatic_field_kraus,
)
from ic_quantum.core.validation import validate_kraus


def test_physical_source_registry_has_eight_nonredundant_source_families():
    registry = build_physical_source_registry()
    assert registry.list_ids() == (
        "bistable-charge-fluctuator-rtn",
        "external-electromagnetic-rabi-drive",
        "external-magnetic-field-wave",
        "finite-mode-spin-boson-dephasing",
        "ionizing-radiation-quasiparticle-burst",
        "mechanical-phonon-mode",
        "single-mode-mechanical-phonon-dephasing",
        "thermal-photon-reservoir",
    )
    for agent_id in registry.list_ids():
        model = registry.get(agent_id)
        validate_model_record(model)
        assert model.maturity_level is ModelMaturityLevel.LEVEL_3
        assert model.physical_source != "unresolved"
        assert model.causal_mechanism != "unresolved"


def test_radiation_model_is_explicitly_phenomenological_at_source_channel_bridge():
    model = build_physical_source_registry().get(
        "ionizing-radiation-quasiparticle-burst"
    )
    assert any(ref.kind is ProvenanceKind.PHENOMENOLOGICAL for ref in model.references)
    assert "not a microscopic radiation Hamiltonian" in " ".join(model.validity_domain)


def test_external_gaussian_field_is_identity_at_zero_variance_and_cptp():
    assert np.isclose(
        gaussian_quasistatic_field_coherence_factor(
            gyromagnetic_ratio=1.0,
            field_standard_deviation=0.0,
            time=100.0,
        ),
        1.0,
    )
    validate_kraus(
        gaussian_quasistatic_field_kraus(
            gyromagnetic_ratio=2.0,
            field_standard_deviation=0.3,
            time=0.7,
        )
    )


def test_physical_catalog_keeps_channel_names_out_of_agent_identity():
    registry = build_physical_source_registry()
    ids = " ".join(registry.list_ids())
    assert "amplitude-damping" not in ids
    assert "depolarizing" not in ids
    # The spin-boson ID contains "dephasing" only as a dynamical qualifier after the
    # explicit physical source; it is not a bare channel identity.
    assert "dephasing" not in registry.get(
        "bistable-charge-fluctuator-rtn"
    ).agent_id



def test_zero_temperature_photon_baseline_is_not_duplicated_as_v2_agent():
    registry = build_physical_source_registry()
    assert "markovian-photon-reservoir-decay" not in registry.list_ids()
    thermal = registry.get("thermal-photon-reservoir")
    assert "T=0" in " ".join(thermal.validity_domain)
