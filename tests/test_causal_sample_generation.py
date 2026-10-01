import numpy as np

from ic_quantum.data.generator import (
    generate_coherent_detuning_samples,
    generate_exchange_relaxation_samples,
    generate_first_lot_smoke_samples,
)


def _find(samples, model_id, probe, time):
    return next(
        s for s in samples
        if s.agent_model_id == model_id
        and s.initial_system_state == probe
        and np.isclose(s.time, time)
    )


def test_first_lot_smoke_generator_is_small_and_uses_all_probe_axes():
    samples = generate_first_lot_smoke_samples()
    assert len(samples) == 24
    assert {s.initial_system_state for s in samples} == {
        "0", "1", "+", "-", "+i", "-i"
    }
    assert all(s.random_seed is None for s in samples)
    assert all(s.metadata["deterministic"] for s in samples)


def test_default_feature_payload_does_not_leak_model_or_simulator_parameters():
    sample = generate_coherent_detuning_samples(
        detuning=1.0,
        times=(0.7,),
        probe_ids=("+",),
    )[0]
    payload = sample.observable_feature_payload()
    assert "agent_model_id" not in payload
    assert "sample_id" not in payload
    assert "parameter_values" not in payload
    assert "metadata" not in payload


def test_distinct_models_are_explicitly_non_identifiable_at_zero_interaction_time():
    samples = generate_first_lot_smoke_samples()
    coherent = _find(samples, "coherent-longitudinal-detuning", "+i", 0.0)
    exchange = _find(samples, "finite-two-level-exchange-relaxation", "+i", 0.0)

    assert coherent.agent_model_id != exchange.agent_model_id
    assert coherent.observable_feature_payload() == exchange.observable_feature_payload()


def test_models_can_be_distinguished_for_a_selected_nonzero_probe_response():
    coherent = generate_coherent_detuning_samples(
        detuning=1.0, times=(0.7,), probe_ids=("+",)
    )[0]
    exchange = generate_exchange_relaxation_samples(
        coupling=0.4, times=(0.7,), probe_ids=("+",)
    )[0]

    c = coherent.signature.observables
    e = exchange.signature.observables
    assert not np.allclose(
        [c["X"], c["Y"], c["Z"]],
        [e["X"], e["Y"], e["Z"]],
        atol=1e-10,
        rtol=0.0,
    )
