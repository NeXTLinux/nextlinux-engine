---
title: "Using Environment Variables in Nextlinux"
linkTitle: "Environment Variables"
weight: 6
---

Environment variable references may be used in the Nextlinux config.yaml file to set values that need to be configurable during deployment.

Using this mechanism a common configuration file can be used with multiple Nextlinux Engine instances with key values being passed using environment variables.

The config.yaml configuration file is read by the Nextlinux Engine any references to variables prefixed with NEXTLINUX will be replaced by the value of the matching environment variable.

For example in the sample configuration file the _host_id_ parameter is set be appending the NEXTLINUX_HOST_ID variable to the string _dockerhostid_

`host_id: 'dockerhostid-${NEXTLINUX_HOST_ID}'`

Notes:

1. Only variables prefixed with NEXTLINUX will be replaced
2. If an environment variable is referenced in the configuration file but not set in the environment then a warning will be logged
3. It is recommend to use curly braces, for example ${NEXTLINUX_PARAM} to avoid potentially ambiguous cases

### Passing Environment Variables as a File

Environment Variables may also be passed as a file contained key value pairs.

```
NEXTLINUX_HOST_ID=myservice1
NEXTLINUX_LOG_LEVEL=DEBUG
```

The Nextlinux Engine will check for an environment variable named _NEXTLINUX_ENV_FILE_ if this variable is set the the Nextlinux Engine will attempt to read a file at the location specified in this variable.

The Nextlinux environment file is read before any other Nextlinux environment variables so any NEXTLINUX variables passed in the environment will override the values set in the environment file.
