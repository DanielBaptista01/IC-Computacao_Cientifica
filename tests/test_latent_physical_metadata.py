import numpy as np

from ic_quantum.dynamics.causal_latent import (
    LatentCausalTransform,
    LatentTransformKind,
)


def test_latent_causal_transform_carries_physical_source_metadata_explicitly():
    latent = LatentCausalTransform(
        transform_id="em-between-depths",
        depth_after=2,
        kind=LatentTransformKind.UNITARY,
        dimension=2,
        unitary=np.eye(2, dtype=complex),
        agent_id="external-electromagnetic-rabi-drive",
        physical_source="external coherent electromagnetic wave",
        coupling_mechanism="effective Rabi coupling",
        physical_parameters={"rabi_rate": 1.0},
        interaction_time=0.5,
        effective_channel="coherent unitary Rabi rotation",
        provenance=("Norambuena, Tancara and Coto 2020",),
    )
    assert latent.physical_source == "external coherent electromagnetic wave"
    assert latent.physical_parameters["rabi_rate"] == 1.0
    assert latent.interaction_time == 0.5
    assert latent.effective_channel == "coherent unitary Rabi rotation"



def test_latent_physical_interaction_time_must_be_nonnegative():
    import pytest

    with pytest.raises(ValueError, match="interaction_time"):
        LatentCausalTransform(
            transform_id="invalid-negative-time",
            depth_after=0,
            kind=LatentTransformKind.IDENTITY,
            interaction_time=-1.0,
        )
