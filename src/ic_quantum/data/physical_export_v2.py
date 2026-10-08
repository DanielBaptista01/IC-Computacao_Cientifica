"""Compatibility facade for the reconciled physical-source v2 exporter."""

from ic_quantum.data.physical_v2_export import export_physical_v2_dataset


def export_physical_v2(samples, config, output_dir):
    return export_physical_v2_dataset(samples, config, output_dir)


__all__ = ["export_physical_v2", "export_physical_v2_dataset"]
