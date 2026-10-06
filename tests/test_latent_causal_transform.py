import numpy as np

from ic_quantum.channels.dephasing import dephasing_kraus
from ic_quantum.channels.unitary import coherent_z_unitary
from ic_quantum.core.states import reference_density
from ic_quantum.dynamics.causal_latent import (
    LatentCausalTransform,
    LatentTransformKind,
)
from ic_quantum.dynamics.reversibility import (
    max_unitary_recovery_fidelity_to_pure_target,
)
from ic_quantum.metrics.fidelity import fidelity
from ic_quantum.metrics.purity import purity


def test_identity_latent_transform_represents_ideal_interdepth_interval():
    rho = reference_density("+")
    latent = LatentCausalTransform(
        transform_id="C_identity_d1",
        depth_after=1,
        kind=LatentTransformKind.IDENTITY,
        dimension=2,
        agent_id=None,
    )

    assert latent.interval == (1, 2)
    assert np.allclose(latent.apply(rho), rho, atol=1e-10, rtol=0.0)
    assessment = latent.reversibility_assessment()
    assert assessment is not None
    assert assessment.direct_unitary_inverse
    assert np.allclose(latent.direct_unitary_inverse(), np.eye(2), atol=1e-10)


def test_unitary_latent_transform_is_recovered_by_adjoint():
    rho = reference_density("+")
    unitary = coherent_z_unitary(omega=1.0, time=0.7)
    latent = LatentCausalTransform(
        transform_id="C_coherent_z_d1",
        depth_after=1,
        kind=LatentTransformKind.UNITARY,
        dimension=2,
        agent_id="coherent_z",
        parameters={"omega": 1.0, "time": 0.7},
        unitary=unitary,
    )

    perturbed = latent.apply(rho)
    inverse = latent.direct_unitary_inverse()
    assert inverse is not None
    recovered = inverse @ perturbed @ inverse.conjugate().T

    assert np.allclose(recovered, rho, atol=1e-10, rtol=0.0)
    assert np.isclose(fidelity(rho, recovered), 1.0, atol=1e-10)
    assessment = latent.reversibility_assessment()
    assert assessment is not None
    assert assessment.classification == "class_I_direct_unitary_reversible"


def test_kraus_latent_transform_has_no_direct_unitary_inverse():
    rho = reference_density("+")
    latent = LatentCausalTransform(
        transform_id="C_dephasing_d1",
        depth_after=1,
        kind=LatentTransformKind.KRAUS_CPTP,
        dimension=2,
        agent_id="dephasing",
        parameters={"p": 0.35},
        kraus_operators=tuple(dephasing_kraus(0.35)),
    )

    perturbed = latent.apply(rho)
    assessment = latent.reversibility_assessment()

    assert latent.direct_unitary_inverse() is None
    assert assessment is not None
    assert not assessment.direct_unitary_inverse
    assert assessment.linear_invertible
    assert assessment.inverse_cptp is False
    assert purity(perturbed) < purity(rho)

    bound = max_unitary_recovery_fidelity_to_pure_target(perturbed, rho)
    assert np.isclose(bound, 0.825, atol=1e-10)
    assert bound < 1.0
