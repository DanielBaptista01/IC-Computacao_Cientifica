from ic_quantum.agents.canonical import (
    amplitude_damping_agent,
    dephasing_agent,
    depolarizing_agent,
)


def test_canonical_channels_are_explicitly_baselines_not_physical_sources():
    for factory in (dephasing_agent, amplitude_damping_agent, depolarizing_agent):
        baseline = factory(0.2)
        assert baseline.model_role == "channel_baseline"
        assert baseline.physical_source is None
        assert baseline.causal_mechanism == (
            "not specified by the canonical reduced channel"
        )
