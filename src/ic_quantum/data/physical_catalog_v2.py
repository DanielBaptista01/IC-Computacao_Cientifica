"""Compatibility facade for the reconciled physical-source v2 catalog.

The authoritative implementation lives in :mod:`ic_quantum.data.physical_catalog`.
This module preserves the public import path introduced on the parallel main-line
implementation without maintaining a second scientific catalog.
"""

from ic_quantum.data.physical_catalog import (
    bistable_charge_fluctuator_model,
    build_physical_source_registry,
    external_electromagnetic_rabi_model,
    external_magnetic_field_model,
    ionizing_radiation_quasiparticle_model,
    mechanical_longitudinal_phonon_model,
    mechanical_phonon_mode_model,
    thermal_photon_reservoir_model,
)


def build_physical_v2_registry():
    return build_physical_source_registry()


# Historical main-line name mapped to the authoritative magnetic source family.
external_magnetic_zeeman_model = external_magnetic_field_model
single_mode_mechanical_phonon_model = mechanical_longitudinal_phonon_model
external_electromagnetic_drive_model = external_electromagnetic_rabi_model

__all__ = [
    "build_physical_v2_registry",
    "build_physical_source_registry",
    "external_electromagnetic_drive_model",
    "external_electromagnetic_rabi_model",
    "external_magnetic_zeeman_model",
    "external_magnetic_field_model",
    "thermal_photon_reservoir_model",
    "single_mode_mechanical_phonon_model",
    "mechanical_longitudinal_phonon_model",
    "mechanical_phonon_mode_model",
    "ionizing_radiation_quasiparticle_model",
    "bistable_charge_fluctuator_model",
]
