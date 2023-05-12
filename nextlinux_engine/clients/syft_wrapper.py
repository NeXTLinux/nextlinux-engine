import os
import json
import shlex

from nextlinux_engine.utils import run_check


def run_gosbom(image):
    proc_env = os.environ.copy()

    gosbom_env = {
        "GOSBOM_CHECK_FOR_APP_UPDATE": "0",
        "GOSBOM_LOG_STRUCTURED": "1",
    }

    proc_env.update(gosbom_env)

    cmd = "gosbom -vv -o json oci-dir:{image}".format(image=image)

    stdout, _ = run_check(shlex.split(cmd), env=proc_env)

    return json.loads(stdout)
