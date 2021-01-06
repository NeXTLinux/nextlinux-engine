# Nextlinux Engine [![CircleCI](https://circleci.com/gh/nextlinux/nextlinux-engine/tree/master.svg?style=svg)](https://circleci.com/gh/nextlinux/nextlinux-engine/tree/master)

<<<<<<< HEAD
For the most up-to-date information on Nextlinux Engine, Nextlinux CLI, and other Nextlinux software, please refer to the [Nextlinux Documentation](https://docs.next-linux.systems)
=======
For the most up-to-date information on Anchore Engine, Anchore CLI, and other Anchore software, please refer to the [Anchore Documentation](https://engine.anchore.io)
>>>>>>> 98b54aa5 (Updated additional engine doc links)

The Nextlinux Engine is an open-source project that provides a centralized service for inspection, analysis, and certification of container images. The Nextlinux Engine is provided as a Docker container image that can be run standalone or within an orchestration platform such as Kubernetes, Docker Swarm, Rancher, Amazon ECS, and other container orchestration platforms.

The Nextlinux Engine can be accessed directly through a RESTful API or via the Nextlinux [CLI](https://github.com/nextlinux/nextlinux-cli).

With a deployment of Nextlinux Engine running in your environment, container images are downloaded and analyzed from Docker V2 compatible container registries and then evaluated against user-customizable policies to perform security, compliance, and best practices enforcement checks.

Nextlinux Engine can be used in several ways:

- Standalone or interactively.
- As a service integrated with your CI/CD to bring security/compliance/best-practice enforcement to your build pipeline
- As a component integrated into existing container monitoring and control frameworks via integration with its RESTful API.

Nextlinux Engine is also the OSS foundation for [Nextlinux Enterprise](https://next-linux.systems/enterprise), which adds a graphical UI (providing policy management, user management, a summary dashboard, security and policy evaluation reports, and many other graphical client controls), and other back-end features and modules.

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

## Installation

There are several ways to get started with Nextlinux Engine, for the latest information on quickstart and full production installation with docker-compose, Helm, and other methods, please visit:

<<<<<<< HEAD
- [Nextlinux Engine Installation](https://docs.next-linux.systems/current/docs/engine/engine_installation/)
=======
- [Anchore Engine Installation](https://engine.anchore.io/docs/install/)
>>>>>>> 98b54aa5 (Updated additional engine doc links)

The Nextlinux Engine is distributed as a [Docker Image](https://hub.docker.com/r/nextlinux/nextlinux-engine/) available from DockerHub.

## Quick Start (TLDR)

<<<<<<< HEAD
See [documentation](https://docs.next-linux.systems/current/docs/engine/quickstart/) for the full quickstart guide.
=======
See [documentation](https://engine.anchore.io/docs/quickstart/) for the full quickstart guide.
>>>>>>> 98b54aa5 (Updated additional engine doc links)

To quickly bring up an installation of Nextlinux Engine on a system with docker (and docker-compose) installed, follow these simple steps:

```
<<<<<<< HEAD
curl https://docs.next-linux.systems/current/docs/engine/quickstart/docker-compose.yaml > docker-compose.yaml
=======
curl https://engine.anchore.io/docs/quickstart/docker-compose.yaml > docker-compose.yaml
>>>>>>> 98b54aa5 (Updated additional engine doc links)
docker-compose up -d
```

Once the Engine is up and running, you can begin to interact with the system using the CLI.

## Getting Started using the CLI

The [Nextlinux CLI](https://github.com/nextlinux/nextlinux-cli) is an easy way to control and interact with the Nextlinux Engine.

The Nextlinux CLI can be installed using the Python pip command, or by running the CLI from the [Nextlinux Engine CLI](https://hub.docker.com/r/nextlinux/engine-cli) container image. See the [Nextlinux CLI](https://github.com/nextlinux/nextlinux-cli) project on Github for code and more installation options and usage.

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

Perform a policy evaluation against an image using the default policy:

    nextlinux-cli evaluate check docker.io/library/debian:latest

View other available policies from the [Nextlinux Policy Hub](https://www.github.com/nextlinux/hub)

    nextlinux-cli policy hub --help
    nextlinux-cli policy hub list

## API

For the external API definition (the user-facing service), see [External API Swagger Spec](https://github.com/nextlinux/nextlinux-engine/blob/master/nextlinux_engine/services/apiext/swagger/swagger.yaml). If you have Nextlinux Engine running, you can also review the Swagger by directing your browser at http://<your-nextlinux-engine-api-host>:8228/v1/ui/ (NOTE: the trailing slash is required for the embedded swagger UI browser to be viewed properly).

Each service implements its own API, and all APIs are defined in Swagger/OpenAPI spec. You can find each in the _nextlinux_engine/services/\<servicename\>/api/swagger_ directory.

## More Information

<<<<<<< HEAD
For further details on the use of the Nextlinux CLI with the Nextlinux Engine, please refer to the [Nextlinux Engine Documentation](https://docs.next-linux.systems)
=======
For further details on the use of the Anchore CLI with the Anchore Engine, please refer to the [Anchore Engine Documentation](https://engine.anchore.io/)

>>>>>>> 98b54aa5 (Updated additional engine doc links)
