---
title: "Configuring the Nextlinux CLI"
weight: 1
---

By default the Nextlinux CLI will try to connect to the Nextlinux Engine at http://localhost/v1 with no authentication.

The username, password and URL for the server can be passed to the Nextlinux CLI using one of three methods:

### Command Line Parameters

The following command line parameters are used to configure the Nextlinux CLI to connect to and authenticate with the Nextlinux Engine.

```
--u   TEXT   Username     eg. admin
--p   TEXT   Password     eg. foobar
--url TEXT   Service URL  eg. http://localhost:8228/v1
--insecure  Skip certificate validation checks (optional)
```

These connection parameters should be passed before any other commands.
eg.

`$ nextlinux-cli --u admin --p foobar --url http://nextlinux.example.com:8228/v1`

### Environment Variables

Rather than passing command line parameters for every call to the Nextlinux CLI they can be stored as environment variables.

```
NEXTLINUX_CLI_URL=http://myserver.example.com:8228/v1
NEXTLINUX_CLI_USER=admin
NEXTLINUX_CLI_PASS=foobar
NEXTLINUX_CLI_SSL_VERIFY=n
```

### Credentials File (recommended)

The server URL and authentications credentials can be stored in a configuration file stored in the user's home directory.

The file should be stored in the following location: $HOME/.nextlinux/credentials.yaml

```
default:
        NEXTLINUX_CLI_USER: 'admin'
        NEXTLINUX_CLI_PASS: 'foobar'
        NEXTLINUX_CLI_URL: 'http://localhost:8228/v1'
```

### Order or Precedence

The Nextlinux CLi will first look for configuration via command line parameters. If no command line parameters are passed then the environment is checked, finally the CLI will check for a credentials file.

**Note:** All examples in the documentation will presume that the credentials have been configured using either environment variables or the credentials file.
