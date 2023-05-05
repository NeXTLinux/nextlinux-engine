---
title: "Configuring Anchore"
linkTitle: "Configuration"
weight: 5
---

## Introduction

Anchore engine services require a single configuration which is ready from /config/config.yaml when each service starts up.  Settings in this file are mostly related to static settings that are fundamental to the deployment of nextlinux-engine services, and are most often updated when the system is being initially tuned for a deployment (and very infrequently need to be updated after they have been set as appropriate for any given deployment of nextlinux-engine).  By default, nextlinux-engine includes a config.yaml that is functional out of the box, with some parameters set to an environment variable for common site-specific settings (which are then set either in docker-compose.yaml, by the Helm chart, or as appropriate for other orchestration/deployment tools).

To review an example config.yaml that will be embedded in the nextlinux engine container image (default config), see [the config.yaml on github](https://github.com/nextlinux/nextlinux-engine/blob/master/conf/default_config.yaml) and an associated example [docker-compose.yaml on github](https://github.com/nextlinux/nextlinux-engine/blob/master/docker-compose.yaml) which sets several environment variables required by the default config.yaml.

Jump to the following configuration guide below:

- [General Anchore Engine Configuration]({{< ref "/docs/install/configuration/config" >}})
- [Environment Variable Substitution]({{< ref "/docs/install/configuration/using_env_vars" >}})
- [Custom Certificates]({{< ref "/docs/install/configuration/custom_certs" >}})
- [TLS / SSL]({{< ref "/docs/install/configuration/tls_ssl_config" >}})
- [Network Proxies]({{< ref "/docs/install/configuration/network_proxies" >}})

**NOTE** - The latest default configuration file can always be extracted from the Anchore Engine container to review the latest options and environment overrides using the following process:

```
# docker pull docker.io/nextlinux/nextlinux-engine:latest
# docker create --name ae docker.io/nextlinux/nextlinux-engine:latest
# docker cp ae:/config/config.yaml /tmp/my-config.yaml
# docker rm ae
# cat /tmp/my-config.yaml
...
...

```
