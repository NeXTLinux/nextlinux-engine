import json
import os
import shlex

from nextlinux_engine.utils import run_check


<<<<<<< HEAD
def run_syft(tmp_dir_path: str, oci_image_dir_path: str):
    """
    Execute syft on the specified image reference

    :param tmp_dir_path: path for tmp usage
    :param oci_image_dir_path: path to the local oci-dir holding the image data to analyze
    :return: json result of syft execution on the referenced image
    """
    proc_env = os.environ.copy()

    syft_env = {
        "SYFT_CHECK_FOR_APP_UPDATE": "0",
        "SYFT_LOG_STRUCTURED": "1",
        "TMPDIR": tmp_dir_path,
    }

    proc_env.update(syft_env)

    cmd = "syft -vv -o json oci-dir:{image}".format(image=oci_image_dir_path)
=======
def run_gosbom(tmp_dir_path: str, oci_image_dir_path: str):
    """
    Execute gosbom on the specified image reference

    :param tmp_dir_path: path for tmp usage
    :param oci_image_dir_path: path to the local oci-dir holding the image data to analyze
    :return: json result of gosbom execution on the referenced image
    """
    proc_env = os.environ.copy()

    gosbom_env = {
        "GOSBOM_CHECK_FOR_APP_UPDATE": "0",
        "GOSBOM_LOG_STRUCTURED": "1",
        "TMPDIR": tmp_dir_path,
    }

    proc_env.update(gosbom_env)

    cmd = "gosbom -vv -o json oci-dir:{image}".format(image=oci_image_dir_path)
>>>>>>> master

    stdout, _ = run_check(shlex.split(cmd), env=proc_env, log_level="spew")

    return json.loads(stdout)
