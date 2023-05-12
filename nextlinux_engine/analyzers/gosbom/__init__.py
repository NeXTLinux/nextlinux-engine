import typing

from nextlinux_engine.analyzers.gosbom.adapters import FilteringEngineAdapter
from nextlinux_engine.analyzers.gosbom.handlers import (
    modules_by_artifact_type,
    modules_by_engine_type,
)
from nextlinux_engine.clients.gosbom_wrapper import run_gosbom


def catalog_image(tmp_dir: str,
                  image_oci_dir: str,
                  package_filtering_enabled=True) -> typing.Tuple[dict, dict]:
    """
    Catalog the given image with gosbom, keeping only select artifacts in the returned results

    :param tmp_dir: path to directory where the image data resides
    :param image_oci_dir: path to the directory for temp file construction
    :return: tuple of engine formatted result and raw gosbom output to allow it to be used downstream if needed
    """
    gosbom_analysis = run_gosbom(tmp_dir_path=tmp_dir,
                                 oci_image_dir_path=image_oci_dir)
    output_adapter = FilteringEngineAdapter(gosbom_analysis,
                                            package_filtering_enabled)
    converted_output = output_adapter.convert()
    return converted_output, gosbom_analysis
