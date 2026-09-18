import numpy as np

from ic_quantum.experiments.runner import run_first_experiment


def test_first_experiment_records_reversibility_distinctions():
    dataframe = run_first_experiment()

    assert len(dataframe) == 16
    required = {
        "linear_invertible",
        "inverse_cptp",
        "direct_unitary_inverse",
        "superoperator_condition_number",
        "reversibility_class",
    }
    assert required.issubset(dataframe.columns)

    coherent = dataframe[dataframe["agent_id"] == "coherent_z"]
    assert coherent["direct_unitary_inverse"].all()
    assert coherent["linear_invertible"].all()
    assert coherent["inverse_cptp"].all()
    assert np.allclose(coherent["recovery_fidelity"], 1.0, atol=1e-10)

    for agent_id in ("dephasing", "amplitude_damping"):
        subset = dataframe[dataframe["agent_id"] == agent_id]
        assert subset["linear_invertible"].all()
        assert not subset["direct_unitary_inverse"].any()
        assert not subset["inverse_cptp"].any()
        assert set(subset["reversibility_class"]) == {
            "class_II_linearly_invertible_without_CPTP_inverse"
        }
