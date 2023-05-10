ARG BASE_REGISTRY=registry.access.redhat.com
ARG BASE_IMAGE=ubi8/ubi
ARG BASE_TAG=8.5

#### Start first stage
#### Nextlinux wheels, binary dependencies, etc. are staged to /build_output for second stage
FROM ${BASE_REGISTRY}/${BASE_IMAGE}:${BASE_TAG} as nextlinux-engine-builder

ARG CLI_COMMIT

ENV LANG=en_US.UTF-8 
ENV LC_ALL=C.UTF-8

# environment variables for dependent binary versions
ENV GOSBOM_VERSION=v0.33.0
ENV GOVULNERS_VERSION=v0.27.3
ENV PIP_VERSION=21.0.1

# setup build artifact directory
RUN set -ex && \
    mkdir -p \
        /build_output/configs \
        /build_output/cli_wheels \
        /build_output/deps \
        /build_output/wheels

# installing build dependencies
RUN set -ex && \
    echo "installing build dependencies" && \
    # keepcache is used so that subsequent invocations of yum do not remove the cached RPMs in --downloaddir
    echo "keepcache = 1" >> /etc/yum.conf && \
    yum update -y && \
    yum module disable -y python36 && \
    yum module enable -y python38 && \
    yum install -y \
        gcc \
        git \
        go \
        make \
        python38 \
        python38-devel \
        python38-psycopg2 \
        python38-wheel && \
    yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && \
    pip3 install pip=="${PIP_VERSION}"

# stage dependent binaries into /build_output
RUN set -ex && \
    echo "downloading OS dependencies" && \
    pip3 download -d /build_output/wheels pip=="${PIP_VERSION}" && \
    yum install -y --downloadonly --downloaddir=/build_output/deps/ \
        clamav \
        clamav-update \
        dpkg

RUN set -ex && \
    echo "downloading nextlinux-cli" && \
    pip3 wheel --wheel-dir=/build_output/cli_wheels/ git+https://github.com/nextlinux/nextlinux-cli.git@"${CLI_COMMIT}"\#egg=nextlinuxcli

RUN set -exo pipefail && \
    echo "downloading Syft" && \
    curl -sSfL https://raw.githubusercontent.com/nextlinux/gosbom/main/install.sh | sh -s -- -b /build_output/deps "${GOSBOM_VERSION}"

RUN set -exo pipefail && \
    echo "downloading Govulners" && \
    curl -sSfL https://raw.githubusercontent.com/nextlinux/govulners/main/install.sh | sh -s -- -b /build_output/deps "${GOVULNERS_VERSION}"

COPY . /buildsource
WORKDIR /buildsource

# stage nextlinux-engine wheels and default application configs into /build_output
RUN set -ex && \
    echo "creating nextlinux-engine wheels" && \
    pip3 wheel --wheel-dir=/build_output/wheels . && \
    cp ./LICENSE /build_output/ && \
    cp ./conf/default_config.yaml /build_output/configs/default_config.yaml && \
    cp ./docker-entrypoint.sh /build_output/configs/docker-entrypoint.sh

# create p1 buildblob & checksum
RUN set -ex && \
    tar -z -c -v -C /build_output -f /nextlinux-buildblob.tgz . && \
    sha256sum /nextlinux-buildblob.tgz > /buildblob.tgz.sha256sum

#### Start second stage
#### Setup and install using first stage artifacts in /build_output
FROM ${BASE_REGISTRY}/${BASE_IMAGE}:${BASE_TAG} as nextlinux-engine-final

ARG CLI_COMMIT
ARG NEXTLINUX_COMMIT
ARG NEXTLINUX_ENGINE_VERSION="1.1.0"
ARG NEXTLINUX_ENGINE_RELEASE="r0"

# Container metadata section
LABEL nextlinux_cli_commit="${CLI_COMMIT}" \
      nextlinux_commit="${NEXTLINUX_COMMIT}" \
      name="nextlinux-engine" \
      maintainer="dev@nextlinux.com" \
      vendor="Nextlinux Inc." \
      version="${NEXTLINUX_ENGINE_VERSION}" \
      release="${NEXTLINUX_ENGINE_RELEASE}" \
      summary="Nextlinux Engine - container image scanning service for policy-based security, best-practice and compliance enforcement." \
      description="Nextlinux is an open platform for container security and compliance that allows developers, operations, and security teams to discover, analyze, and certify container images on-premises or in the cloud. Nextlinux Engine is the on-prem, OSS, API accessible service that allows ops and developers to perform detailed analysis, run queries, produce reports and define policies on container images that can be used in CI/CD pipelines to ensure that only containers that meet your organization’s requirements are deployed into production."

# Environment variables to be present in running environment
ENV AUTHLIB_INSECURE_TRANSPORT=true
ENV LANG=en_US.UTF-8 
ENV LC_ALL=C.UTF-8
ENV PATH="${PATH}:/nextlinux-cli/bin"
ENV SET_HOSTID_TO_HOSTNAME=false

# Default values overrideable at runtime of the container
ENV NEXTLINUX_ADMIN_EMAIL=admin@mynextlinux \
    NEXTLINUX_ADMIN_PASSWORD=null \
    NEXTLINUX_AUTH_ENABLE_HASHED_PASSWORDS=false \
    NEXTLINUX_AUTH_PRIVKEY=null \
    NEXTLINUX_AUTH_PUBKEY=null \
    NEXTLINUX_AUTH_SECRET=null \
    NEXTLINUX_AUTHZ_HANDLER=native \
    NEXTLINUX_CATALOG_NOTIFICATION_INTERVAL_SEC=30 \
    NEXTLINUX_CLI_PASS=foobar \
    NEXTLINUX_CLI_USER=admin \
    NEXTLINUX_CLI_URL="http://localhost:8228" \
    NEXTLINUX_CONFIG_DIR=/config \
    NEXTLINUX_DB_NAME=postgres \
    NEXTLINUX_DB_PORT=5432 \
    NEXTLINUX_DB_USER=postgres \
    NEXTLINUX_DISABLE_METRICS_AUTH=false \
    NEXTLINUX_ENABLE_METRICS=false \
    NEXTLINUX_ENABLE_PACKAGE_FILTERING="true" \
    NEXTLINUX_ENDPOINT_HOSTNAME=localhost \
    NEXTLINUX_EVENTS_NOTIFICATIONS_ENABLED=false \
    NEXTLINUX_EXTERNAL_AUTHZ_ENDPOINT=null \
    NEXTLINUX_EXTERNAL_PORT=null \
    NEXTLINUX_EXTERNAL_TLS=false \
    NEXTLINUX_FEEDS_CLIENT_URL="https://ancho.re/v1/account/users" \
    NEXTLINUX_FEEDS_ENABLED=true \
    NEXTLINUX_FEEDS_SSL_VERIFY=true \
    NEXTLINUX_FEED_SYNC_INTERVAL_SEC=21600 \
    NEXTLINUX_FEEDS_TOKEN_URL="https://ancho.re/oauth/token" \
    NEXTLINUX_FEEDS_URL="https://ancho.re/v1/service/feeds" \
    NEXTLINUX_GLOBAL_CLIENT_CONNECT_TIMEOUT=0 \
    NEXTLINUX_GLOBAL_CLIENT_READ_TIMEOUT=0 \
    NEXTLINUX_GLOBAL_SERVER_REQUEST_TIMEOUT_SEC=180 \
    NEXTLINUX_GOVULNERS_DB_URL="https://toolbox-data.nextlinux.io/govulners/databases/listing.json" \
    NEXTLINUX_HINTS_ENABLED=false \
    NEXTLINUX_HOST_ID="nextlinux-quickstart" \
    NEXTLINUX_INTERNAL_SSL_VERIFY=false \
    NEXTLINUX_LOG_LEVEL=INFO \
    NEXTLINUX_MAX_COMPRESSED_IMAGE_SIZE_MB=-1 \
    NEXTLINUX_OAUTH_ENABLED=false \
    NEXTLINUX_OAUTH_TOKEN_EXPIRATION=3600 \
    NEXTLINUX_SERVICE_DIR=/nextlinux_service \
    NEXTLINUX_SERVICE_PORT=8228 \
    NEXTLINUX_VULNERABILITIES_PROVIDER=null \
    NEXTLINUX_WEBHOOK_DESTINATION_URL=null

#### Perform OS setup

# Setup container user/group and required application directories
RUN set -ex && \
    groupadd --gid 1000 nextlinux && \
    useradd --uid 1000 --gid nextlinux --shell /bin/bash --create-home nextlinux && \
    mkdir -p \
        /analysis_scratch \
        "${NEXTLINUX_SERVICE_DIR}"/bundles \
        /config \
        /home/nextlinux/clamav/db \
        /licenses \
        /var/log/nextlinux \
        /var/run/nextlinux \
        /workspace \
        /workspace_preload && \
    chown -R 1000:0 \
        /analysis_scratch \
        "${NEXTLINUX_SERVICE_DIR}" \
        /config \
        /home/nextlinux \
        /licenses \
        /var/log/nextlinux \
        /var/run/nextlinux \
        /workspace \
        /workspace_preload && \
    chmod -R g+rwX \
        /analysis_scratch \
        "${NEXTLINUX_SERVICE_DIR}" \
        /config \
        /home/nextlinux \
        /licenses \
        /var/log/nextlinux \
        /var/run/nextlinux \
        /workspace \
        /workspace_preload

# Install build dependencies
RUN set -ex && \
    yum update -y && \
    yum module disable -y python36 && \
    yum module enable -y python38 && \
    yum install -y \
        procps \
        psmisc \
        python38 \
        python38-psycopg2 \
        python38-wheel \
        skopeo && \
    yum clean all

# Copy the installed artifacts from the first stage
COPY --from=nextlinux-engine-builder /build_output /build_output

# Install nextlinux-cli into a virtual environment
RUN set -ex && \
    echo "updating pip" && \
    pip3 install --upgrade --no-index --find-links=/build_output/wheels/ pip && \
    echo "installing nextlinux-cli into virtual environment" && \
    python3 -m venv /nextlinux-cli && \
    source /nextlinux-cli/bin/activate && \
    pip3 install --no-index --find-links=/build_output/cli_wheels/ nextlinuxcli && \
    deactivate

# Install required OS deps & application config files
RUN set -exo pipefail && \
    cp /build_output/deps/gosbom /usr/bin/gosbom && \
    cp /build_output/deps/govulners /usr/bin/govulners && \
    yum install -y /build_output/deps/*.rpm && \
    yum clean all

# Install nextlinux-engine & cleanup filesystem
RUN set -ex && \
    echo "installing nextlinux-engine and required dependencies" && \
    pip3 install --no-index --find-links=/build_output/wheels/ nextlinux-engine && \
    echo "copying default application config files" && \
    cp /build_output/LICENSE /licenses/ && \
    cp /build_output/configs/default_config.yaml /config/config.yaml && \
    md5sum /config/config.yaml > /config/build_installed && \
    cp /build_output/configs/docker-entrypoint.sh /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh && \
    cp -R $(pip3 show nextlinux-engine | grep Location: | cut -c 11-)/nextlinux_engine/conf/clamav/freshclam.conf /home/nextlinux/clamav/ && \
    chmod -R ug+rw /home/nextlinux/clamav && \
    echo "cleaning up unneccesary files used for testing/cache/build" && \
    rm -rf \
        /build_output \
        /root/.cache \
        /usr/local/lib64/python3.8/site-packages/twisted/test \
        /usr/local/lib64/python3.8/site-packages/Crypto/SelfTest \
        /usr/share/doc

# Container runtime instructions

HEALTHCHECK --start-period=20s \
    CMD curl -f http://localhost:8228/health || exit 1

USER 1000

EXPOSE "${NEXTLINUX_SERVICE_PORT}"

WORKDIR /nextlinux-engine

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nextlinux-manager", "service", "start", "--all"]
