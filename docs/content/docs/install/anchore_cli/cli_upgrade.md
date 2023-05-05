---
title: "Upgrading the Nextlinux CLI"
weight: 1
---

The Nextlinux CLI is published as a Python Package that can be installed from source from the Python PyPI package repository on any platform supporting PyPi. Upgrades to the Nextlinux CLI are performed using the identical method used for installation.

`$ pip install --user --upgrade nextlinuxcli`

To check if an update is available from the PyPI package repository run the following command:

```
$ pip search nextlinuxcli
nextlinuxcli (0.2.0)  - Nextlinux Service CLI
  INSTALLED: 0.1.10
  LATEST:    0.2.0
```

In this example the pip search command shows that we have nextlinuxcli version 0.1.10 installed however the latest available version is 0.2.0.

**Note:** Python package names cannot include a dash so while the command name is nextlinux-cli the PyPi packages is nextlinuxcli.