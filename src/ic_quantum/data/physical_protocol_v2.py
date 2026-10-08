"""Compatibility facade for the reconciled physical-source v2 protocol."""

from ic_quantum.data.physical_v2_protocol import (
    PhysicalV2Config,
    load_physical_v2_config,
)

__all__ = ["PhysicalV2Config", "load_physical_v2_config"]
