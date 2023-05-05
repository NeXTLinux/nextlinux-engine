#!/usr/bin/python
from setuptools import setup, find_packages
import os, shutil, errno, re
from nextlinux_engine import version

version = version.version
package_name = "nextlinux_engine"
description = "Nextlinux Engine"
long_description = open("README.md").read()
url = "http://www.next-linux.systems"

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# find all the swaggers
swaggers = []
for root, dirnames, filenames in os.walk("./" + package_name):
    if "swagger.yaml" in filenames:
        theswaggerdir = re.sub(re.escape("./" + package_name + "/"), "", root)
        swaggers.append("/".join([theswaggerdir, "swagger.yaml"]))

package_data = {
    package_name: [
        "conf/*",
        "conf/bundles/*",
        "analyzers/modules/*",
    ]
    + swaggers,
    "twisted": ["plugins/*"],
}

data_files = []
# scripts = ['scripts/nextlinux-engine']
scripts = []
packages = find_packages(exclude=["test", "test.*"])
packages.append("twisted.plugins")
setup(
    name="nextlinux_engine",
    author="Nextlinux Inc.",
    author_email="dev@next-linux.systems",
    license="Apache License 2.0",
    description=description,
    long_description=long_description,
    url=url,
    packages=packages,
    version=version,
    data_files=data_files,
    include_package_data=True,
    package_data=package_data,
    install_requires=requirements,
    scripts=scripts,
    entry_points="""
    [console_scripts]
    nextlinux-manager=nextlinux_manager.cli:main_entry
    """,
)
