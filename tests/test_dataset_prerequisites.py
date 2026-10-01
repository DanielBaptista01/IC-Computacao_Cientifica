import numpy as np
import pytest

from ic_quantum.core.probes import standard_probe_densities
from ic_quantum.data.causal_agent_schema import MemoryRegime
from ic_quantum.data.initial_catalog import coherent_detuning_model
from ic_quantum.dynamics.reversibility import (
    max_unitary_recovery_fidelity_to_pure_target,
)
from ic_quantum.metrics.distance import trace_distance


def test_closed_coherent_model_does_not_misuse_markovian_label():
    model = coherent_detuning_model()
    assert model.memory_regime is MemoryRegime.NOT_APPLICABLE


def test_trace_distance_has_expected_extremes_for_qubit_reference_states():
    probes = standard_probe_densities()
    assert np.isclose(trace_distance(probes["0"], probes["0"]), 0.0)
    assert np.isclose(trace_distance(probes["0"], probes["1"]), 1.0)


def test_trace_distance_rejects_dimension_mismatch():
    qubit = standard_probe_densities()["0"]
    qutrit = np.diag([1.0, 0.0, 0.0]).astype(complex)
    with pytest.raises(ValueError):
        trace_distance(qubit, qutrit)


def test_unitary_recovery_bound_rejects_dimension_mismatch():
    qubit = standard_probe_densities()["0"]
    qutrit_target = np.diag([1.0, 0.0, 0.0]).astype(complex)
    with pytest.raises(ValueError):
        max_unitary_recovery_fidelity_to_pure_target(qubit, qutrit_target)
