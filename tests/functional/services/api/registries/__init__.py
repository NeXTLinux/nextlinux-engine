import os


def get_registry_info():
    return {
        "user": os.environ["NEXTLINUX_TEST_DOCKER_REGISTRY_USER"],
        "pass": os.environ["NEXTLINUX_TEST_DOCKER_REGISTRY_PASS"],
        "host": os.environ["NEXTLINUX_TEST_DOCKER_REGISTRY_HOST"],
        "service_name": "docker-registry:5000",
    }
