"""Compatibility tests for the parallel v2 API paths merged into main."""

from ic_quantum.data.physical_catalog import build_physical_source_registry
from ic_quantum.data.physical_catalog_v2 import build_physical_v2_registry
from ic_quantum.data.physical_protocol_v2 import PhysicalV2Config
from ic_quantum.data.physical_generator_v2 import generate_physical_v2_samples
from ic_quantum.data.physical_export_v2 import export_physical_v2


def test_parallel_catalog_path_resolves_to_authoritative_nine_family_registry():
    canonical = build_physical_source_registry()
    compatibility = build_physical_v2_registry()
    assert compatibility.list_ids() == canonical.list_ids()
    assert len(compatibility.list_ids()) == 9


def test_parallel_v2_api_symbols_remain_available():
    assert PhysicalV2Config is not None
    assert callable(generate_physical_v2_samples)
    assert callable(export_physical_v2)
