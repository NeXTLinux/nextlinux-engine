import collections

<<<<<<< HEAD:nextlinux_engine/analyzers/gosbom/__init__.py
from nextlinux_engine.analyzers.utils import defaultdict_to_dict, content_hints
from nextlinux_engine.clients.gosbom_wrapper import run_gosbom
from .handlers import handlers_by_artifact_type, handlers_by_engine_type
=======
from nextlinux_engine.analyzers.utils import defaultdict_to_dict, content_hints
from nextlinux_engine.clients.gosbom_wrapper import run_gosbom
from .handlers import modules_by_artifact_type, modules_by_engine_type
>>>>>>> 6db48a19 (Merge v0.9.0 (#830)):nextlinux_engine/analyzers/gosbom/__init__.py


def filter_artifacts(artifact):
    return artifact["type"] in modules_by_artifact_type


def catalog_image(imagedir):
    """
    Catalog the given image with gosbom, keeping only select artifacts in the returned results.
    """
    all_results = run_gosbom(imagedir)
    return convert_gosbom_to_engine(all_results)


def convert_gosbom_to_engine(all_results):
    """
    Do the conversion from gosbom format to engine format

    :param all_results:
    :return:
    """

    # transform output into analyzer-module/service "raw" analyzer json document
    nested_dict = lambda: collections.defaultdict(nested_dict)
    findings = nested_dict()

    # This is the only use case for consuming the top-level results from gosbom,
    # capturing the information needed for BusyBox. No artifacts should be
    # expected, and having outside of the artifacts loop ensure this will only
    # get called once.
    distro = all_results.get("distro")
    if distro and distro.get("name", "").lower() == "busybox":
        findings["package_list"]["pkgs.all"]["base"]["BusyBox"] = distro["version"]
    elif not distro or not distro.get("name"):
        findings["package_list"]["pkgs.all"]["base"]["Unknown"] = "0"

    # take a sub-set of the gosbom findings and invoke the handler function to
    # craft the artifact document and inject into the "raw" analyzer json
    # document
    for artifact in filter(filter_artifacts, all_results["artifacts"]):
        handler = modules_by_artifact_type[artifact["type"]]
        handler.translate_and_save_entry(findings, artifact)

    return defaultdict_to_dict(findings)
