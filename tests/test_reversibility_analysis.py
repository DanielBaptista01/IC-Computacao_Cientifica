import numpy as np
import pytest

from ic_quantum.channels.amplitude_damping import amplitude_damping_kraus
from ic_quantum.channels.dephasing import dephasing_kraus
from ic_quantum.channels.depolarizing import depolarizing_kraus
from ic_quantum.channels.unitary import coherent_z_unitary
from ic_quantum.dynamics.reversibility import (
    assess_kraus_reversibility,
    assess_unitary_reversibility,
)


def test_unitary_channel_has_cptp_inverse_and_direct_unitary_recovery():
    unitary = coherent_z_unitary(omega=1.0, time=0.7)
    assessment = assess_unitary_reversibility(unitary)

    assert assessment.is_cptp
    assert assessment.linear_invertible
    assert assessment.inverse_cptp is True
    assert assessment.direct_unitary_inverse
    assert assessment.choi_rank == 1
    assert np.isclose(assessment.condition_number, 1.0, atol=1e-10)
    assert assessment.classification == "class_I_direct_unitary_reversible"


@pytest.mark.parametrize(
    "factory,p",
    [
        (dephasing_kraus, 0.35),
        (amplitude_damping_kraus, 0.25),
        (depolarizing_kraus, 0.20),
    ],
)
def test_nonunitary_channels_can_be_linearly_invertible_without_cptp_inverse(factory, p):
    assessment = assess_kraus_reversibility(factory(p))

    assert assessment.is_cptp
    assert assessment.linear_invertible
    assert assessment.inverse_cptp is False
    assert not assessment.direct_unitary_inverse
    assert assessment.choi_rank > 1
    assert assessment.condition_number is not None
    assert assessment.classification == "class_II_linearly_invertible_without_CPTP_inverse"


@pytest.mark.parametrize(
    "factory",
    [dephasing_kraus, amplitude_damping_kraus, depolarizing_kraus],
)
def test_maximal_canonical_noise_is_not_linearly_invertible(factory):
    assessment = assess_kraus_reversibility(factory(1.0))

    assert assessment.is_cptp
    assert not assessment.linear_invertible
    assert assessment.inverse_cptp is None
    assert not assessment.direct_unitary_inverse
    assert assessment.condition_number is None
    assert assessment.classification == "class_II_reduced_nonunitary_noninvertible"
