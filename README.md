<<<<<<< HEAD
# Anchore Engine [![CircleCI](https://circleci.com/gh/nextlinux/nextlinux-engine/tree/master.svg?style=svg)](https://circleci.com/gh/nextlinux/nextlinux-engine/tree/master)

**IMPORTANT NOTE**

As of 2023, Anchore Engine is no longer maintained. There will be no future versions released. Users are advised to use [Syft](https://github.com/nextlinux/syft) and [Grype](https://github.com/nextlinux/grype).

For users interested in a supported commercial solution for container scanning and complaiance, [schedule a demo](https://get.nextlinux.com/demo-request/) to see Anchore Enterprise’s broad set of enterprise capabilities including SBOM management, vulnerability management, and compliance management.
=======
# Nextlinux Engine [![CircleCI](https://circleci.com/gh/nextlinux/nextlinux-engine/tree/master.svg?style=svg)](https://circleci.com/gh/nextlinux/nextlinux-engine/tree/master)

**IMPORTANT NOTE**

As of 2023, Nextlinux Engine is no longer maintained. There will be no future versions released. Users are advised to use [Gosbom](https://github.com/nextlinux/gosbom) and [Govulners](https://github.com/nextlinux/govulners).

For users interested in a supported commercial solution for container scanning and complaiance, [schedule a demo](https://get.nextlinux.com/demo-request/) to see Nextlinux Enterprise’s broad set of enterprise capabilities including SBOM management, vulnerability management, and compliance management.
>>>>>>> master

**About**

Nextlinux Engine is an open-source project that provides a centralized service for inspection, analysis, and certification of container images. Nextlinux Engine is provided as a Docker container image that can be run standalone or within an orchestration platform such as Kubernetes, Docker Swarm, Rancher, Amazon ECS, and other container orchestration platforms.

With a deployment of Nextlinux Engine running in your environment, container images are downloaded and analyzed from Docker V2 compatible container registries and then evaluated against a vulnerability database.

<<<<<<< HEAD
Historical documentation is available at [Anchore Documentation](https://engine.nextlinux.io).

Anchore Engine can be accessed directly through a RESTful API or via the Anchore [CLI](https://github.com/nextlinux/nextlinux-cli).
=======
Historical documentation is available at [Nextlinux Documentation](https://engine.next-linux.systems).

Nextlinux Engine can be accessed directly through a RESTful API or via the Nextlinux [CLI](https://github.com/nextlinux/nextlinux-cli).
>>>>>>> master

**Supported Operating Systems**

- Alpine
- Amazon Linux 2
- CentOS
- Debian
- Google Distroless
- Oracle Linux
- Red Hat Enterprise Linux
- Red Hat Universal Base Image (UBI)
- Ubuntu

**Supported Packages**

- GEM
- Java Archive (jar, war, ear)
- NPM
- Python (PIP)
- Go Modules

## Installation

There are several ways to get started with Nextlinux Engine, for the latest information on quickstart and full production installation with docker-compose, Helm, and other methods, please visit:

<<<<<<< HEAD
- [Anchore Engine Installation](https://engine.nextlinux.io/docs/install/)

The Anchore Engine is distributed as a [Docker Image](https://hub.docker.com/r/nextlinux/nextlinux-engine/) available from DockerHub.

## Quick Start (TLDR)

See [documentation](https://engine.nextlinux.io/docs/quickstart/) for the full quickstart guide.
=======
- [Nextlinux Engine Installation](https://engine.next-linux.systems/docs/install/)

The Nextlinux Engine is distributed as a [Docker Image](https://hub.docker.com/r/nextlinux/nextlinux-engine/) available from DockerHub.

## Quick Start (TLDR)

See [documentation](https://engine.next-linux.systems/docs/quickstart/) for the full quickstart guide.
>>>>>>> master

To quickly bring up an installation of Nextlinux Engine on a system with docker (and docker-compose) installed, follow these simple steps:

```
<<<<<<< HEAD
curl https://engine.nextlinux.io/docs/quickstart/docker-compose.yaml > docker-compose.yaml
=======
curl https://engine.next-linux.systems/docs/quickstart/docker-compose.yaml > docker-compose.yaml
>>>>>>> master
docker-compose up -d
```

Once the Engine is up and running, you can begin to interact with the system using the CLI.

## Getting Started using the CLI

<<<<<<< HEAD
The [Anchore CLI](https://github.com/nextlinux/nextlinux-cli) is an easy way to control and interact with the Anchore Engine.

The Anchore CLI can be installed using the Python pip command, or by running the CLI from the [Anchore Engine CLI](https://hub.docker.com/r/nextlinux/engine-cli) container image. See the [Anchore CLI](https://github.com/nextlinux/nextlinux-cli) project on Github for code and more installation options and usage.
=======
The [Nextlinux CLI](https://github.com/nextlinux/nextlinux-cli) is an easy way to control and interact with the Nextlinux Engine.

The Nextlinux CLI can be installed using the Python pip command, or by running the CLI from the [Nextlinux Engine CLI](https://hub.docker.com/r/nextlinux/engine-cli) container image. See the [Nextlinux CLI](https://github.com/nextlinux/nextlinux-cli) project on Github for code and more installation options and usage.
>>>>>>> master

## CLI Quick Start (TLDR)

By default, the Nextlinux CLI tries to connect to the Nextlinux Engine at http://localhost:8228/v1 with no authentication.
The username, password, and URL for the server can be passed to the Nextlinux CLI as command-line arguments:

    --u   TEXT   Username     eg. admin
    --p   TEXT   Password     eg. foobar
    --url TEXT   Service URL  eg. http://localhost:8228/v1

Rather than passing these parameters for every call to the tool, they can also be set as environment variables:

    NEXTLINUX_CLI_URL=http://myserver.example.com:8228/v1
    NEXTLINUX_CLI_USER=admin
    NEXTLINUX_CLI_PASS=foobar

Add an image to the Nextlinux Engine:

    nextlinux-cli image add docker.io/library/debian:latest

Wait for the image to move to the 'analyzed' state:

    nextlinux-cli image wait docker.io/library/debian:latest

List images analyzed by the Nextlinux Engine:

    nextlinux-cli image list

Get image overview and summary information:

    nextlinux-cli image get docker.io/library/debian:latest

List feeds and wait for at least one vulnerability data feed sync to complete. The first sync can take some time (20-30 minutes) after that syncs will only merge deltas.

    nextlinux-cli system feeds list
    nextlinux-cli system wait

Obtain the results of the vulnerability scan on an image:

    nextlinux-cli image vuln docker.io/library/debian:latest os

List operating system packages present in an image:

    nextlinux-cli image content docker.io/library/debian:latest os

## API

<<<<<<< HEAD
For the external API definition (the user-facing service), see [External API Swagger Spec](https://github.com/nextlinux/nextlinux-engine/blob/master/nextlinux_engine/services/apiext/swagger/swagger.yaml). If you have Anchore Engine running, you can also review the Swagger by directing your browser at http://<your-nextlinux-engine-api-host>:8228/v1/ui/ (NOTE: the trailing slash is required for the embedded swagger UI browser to be viewed properly).
=======
For the external API definition (the user-facing service), see [External API Swagger Spec](https://github.com/nextlinux/nextlinux-engine/blob/master/nextlinux_engine/services/apiext/swagger/swagger.yaml). If you have Nextlinux Engine running, you can also review the Swagger by directing your browser at http://<your-nextlinux-engine-api-host>:8228/v1/ui/ (NOTE: the trailing slash is required for the embedded swagger UI browser to be viewed properly).
>>>>>>> master

Each service implements its own API, and all APIs are defined in Swagger/OpenAPI spec. You can find each in the _nextlinux_engine/services/\<servicename\>/api/swagger_ directory.

## More Information

<<<<<<< HEAD
For further details on the use of the Anchore CLI with the Anchore Engine, please refer to the [Anchore Engine Documentation](https://engine.nextlinux.io/)
=======
For further details on the use of the Nextlinux CLI with the Nextlinux Engine, please refer to the [Nextlinux Engine Documentation](https://engine.next-linux.systems/)
>>>>>>> master

## Developing

This repo was reformatted using [Black](https://black.readthedocs.io/en/stable/) in Nov. 2020. This commit can
be ignored in your local environment when using `git blame` since it impacted so many files. To ignore the commit you need
to configure git-blame to use the provided file: .git-blame-ignore-revs as a list of commits to ignore for blame.

Set your local git configuration to use the provided file by running this from within the root of this source tree:
`git config blame.ignoreRevsFile .git-blame-ignore-revs`
