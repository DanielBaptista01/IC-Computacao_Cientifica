import numpy as np

from ic_quantum.dynamics.causal_latent import LatentCausalTransform, LatentTransformKind


def test_latent_causal_transform_carries_physical_source_metadata_explicitly():
    latent=LatentCausalTransform(
        transform_id="em-between-depths",
        depth_after=2,
        kind=LatentTransformKind.UNITARY,
        unitary=np.eye(2,dtype=complex),
        agent_id="external-electromagnetic-rabi-drive",
        physical_source="external_electromagnetic_field",
        coupling_mechanism="effective Rabi coupling",
        physical_parameters={"rabi_rate":1.0},
        provenance=("Norambuena et al. 2020",),
    )
    assert latent.physical_source == "external_electromagnetic_field"
    assert latent.physical_parameters["rabi_rate"] == 1.0
