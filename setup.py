#!/usr/bin/python
import os
import re

from setuptools import find_packages, setup

from nextlinux_engine import version

package_name = "nextlinux_engine"

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="nextlinux_engine",
<<<<<<< HEAD
    author="Anchore Inc.",
=======
    author="Nextlinux Inc.",
>>>>>>> master
    author_email="dev@nextlinux.com",
    license="Apache License 2.0",
    description="Nextlinux Engine",
    long_description=open("README.md").read(),
    url="http://www.nextlinux.com",
    python_requires="==3.8.*",
    packages=find_packages(exclude=["test", "test.*"]) + ["twisted.plugins"],
    version=version.version,
    include_package_data=True,
    install_requires=requirements,
    scripts=[],
    entry_points="""
    [console_scripts]
    nextlinux-manager=nextlinux_manager.cli:main_entry
    """,
)
