FROM registry.access.redhat.com/ubi8/ubi:8.2 as anchore-engine-builder

######## This is stage1 where anchore wheels, binary deps, and any items from the source tree get staged to /build_output ########

ARG CLI_COMMIT

ENV LANG=en_US.UTF-8 LC_ALL=C.UTF-8

ENV GOPATH=/go
ENV SKOPEO_VERSION=v0.1.41

COPY . /buildsource
WORKDIR /buildsource

RUN set -ex && \
    mkdir -p /build_output /build_output/deps /build_output/configs /build_output/wheels

RUN set -ex && \
    echo "installing OS dependencies" && \
    yum update -y && \
    yum install -y gcc make python38 git python38-wheel python38-devel go

# create anchore binaries
RUN set -ex && \
    echo "installing anchore" && \
    pip3 wheel --wheel-dir=/build_output/wheels . && \
    pip3 wheel --wheel-dir=/build_output/wheels/ git+git://github.com/anchore/anchore-cli.git@$CLI_COMMIT\#egg=anchorecli && \
    cp ./LICENSE /build_output/ && \
    cp ./conf/default_config.yaml /build_output/configs/default_config.yaml && \
    cp ./docker-entrypoint.sh /build_output/configs/docker-entrypoint.sh && \
    cp -R ./conf/clamav /build_output/configs/

# stage anchore dependency binaries
RUN set -ex && \
    echo "installing GO" && \
    mkdir -p /go

RUN set -ex && \
    echo "installing Skopeo" && \
    git clone --branch "$SKOPEO_VERSION" https://github.com/containers/skopeo ${GOPATH}/src/github.com/containers/skopeo && \
    cd ${GOPATH}/src/github.com/containers/skopeo && \
    make binary-local DISABLE_CGO=1 && \
    make install-binary && \
    cp /usr/bin/skopeo /build_output/deps/ && \
    cp default-policy.json /build_output/configs/skopeo-policy.json

RUN set -ex && \
    echo "installing Syft" && \
    curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /anchore_engine/bin v0.9.2

# stage RPM dependency binaries
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && \
    yum install -y --downloadonly --downloaddir=/build_output/deps/ dpkg clamav clamav-update

RUN tar -z -c -v -C /build_output -f /anchore-buildblob.tgz .

# Build setup section

FROM registry.access.redhat.com/ubi8/ubi:8.2 as anchore-engine-final

######## This is stage2 which does setup and install entirely from items from stage1's /build_output ########

ARG CLI_COMMIT
ARG NEXTLINUX_COMMIT
ARG NEXTLINUX_ENGINE_VERSION="0.8.2"
ARG NEXTLINUX_ENGINE_RELEASE="r0"

# Copy skopeo artifacts from build step
COPY --from=anchore-engine-builder /build_output /build_output

# Copy syft from build step
COPY --from=anchore-engine-builder /anchore_engine/bin/syft /anchore_engine/bin/syft

# Container metadata section

MAINTAINER dev@anchore.com

LABEL anchore_cli_commit=$CLI_COMMIT \
      anchore_commit=$NEXTLINUX_COMMIT \
      name="anchore-engine" \
      maintainer="dev@anchore.com" \
      vendor="Nextlinux Inc." \
      version=$NEXTLINUX_ENGINE_VERSION \
      release=$NEXTLINUX_ENGINE_RELEASE \
      summary="Nextlinux Engine - container image scanning service for policy-based security, best-practice and compliance enforcement." \
      description="Nextlinux is an open platform for container security and compliance that allows developers, operations, and security teams to discover, analyze, and certify container images on-premises or in the cloud. Nextlinux Engine is the on-prem, OSS, API accessible service that allows ops and developers to perform detailed analysis, run queries, produce reports and define policies on container images that can be used in CI/CD pipelines to ensure that only containers that meet your organization’s requirements are deployed into production."

# Environment variables to be present in running environment
ENV LANG=en_US.UTF-8 LC_ALL=C.UTF-8

# Default values overrideable at runtime of the container
ENV NEXTLINUX_CONFIG_DIR=/config \
    NEXTLINUX_SERVICE_DIR=/anchore_service \
    NEXTLINUX_LOG_LEVEL=INFO \
    NEXTLINUX_ENABLE_METRICS=false \
    NEXTLINUX_DISABLE_METRICS_AUTH=false \
    NEXTLINUX_INTERNAL_SSL_VERIFY=false \
    NEXTLINUX_WEBHOOK_DESTINATION_URL=null \
    NEXTLINUX_HINTS_ENABLED=false \
    NEXTLINUX_FEEDS_ENABLED=true \
    NEXTLINUX_FEEDS_SELECTIVE_ENABLED=true \
    NEXTLINUX_FEEDS_SSL_VERIFY=true \
    NEXTLINUX_ENDPOINT_HOSTNAME=localhost \
    NEXTLINUX_EVENTS_NOTIFICATIONS_ENABLED=false \
    NEXTLINUX_CATALOG_NOTIFICATION_INTERVAL_SEC=30 \
    NEXTLINUX_FEED_SYNC_INTERVAL_SEC=21600 \
    NEXTLINUX_EXTERNAL_PORT=null \
    NEXTLINUX_EXTERNAL_TLS=false \
    NEXTLINUX_AUTHZ_HANDLER=native \
    NEXTLINUX_EXTERNAL_AUTHZ_ENDPOINT=null \
    NEXTLINUX_ADMIN_PASSWORD=foobar \
    NEXTLINUX_ADMIN_EMAIL=admin@myanchore \
    NEXTLINUX_HOST_ID="anchore-quickstart" \
    NEXTLINUX_DB_PORT=5432 \
    NEXTLINUX_DB_NAME=postgres \
    NEXTLINUX_DB_USER=postgres \
    SET_HOSTID_TO_HOSTNAME=false \
    NEXTLINUX_CLI_USER=admin \
    NEXTLINUX_CLI_PASS=foobar \
    NEXTLINUX_SERVICE_PORT=8228 \
    NEXTLINUX_CLI_URL="http://localhost:8228" \
    NEXTLINUX_FEEDS_URL="https://ancho.re/v1/service/feeds" \
    NEXTLINUX_FEEDS_CLIENT_URL="https://ancho.re/v1/account/users" \
    NEXTLINUX_FEEDS_TOKEN_URL="https://ancho.re/oauth/token" \
    NEXTLINUX_GLOBAL_CLIENT_READ_TIMEOUT=0 \
    NEXTLINUX_GLOBAL_CLIENT_CONNECT_TIMEOUT=0 \
    NEXTLINUX_AUTH_PUBKEY=null \
    NEXTLINUX_AUTH_PRIVKEY=null \
    NEXTLINUX_AUTH_SECRET=null \
    NEXTLINUX_OAUTH_ENABLED=false \
    NEXTLINUX_OAUTH_TOKEN_EXPIRATION=3600 \
    NEXTLINUX_AUTH_ENABLE_HASHED_PASSWORDS=false \
    AUTHLIB_INSECURE_TRANSPORT=true
# Insecure transport required in case for things like tls sidecars

# Container run environment settings

#VOLUME /analysis_scratch
EXPOSE ${NEXTLINUX_SERVICE_PORT}

# Build dependencies

RUN set -ex && \
    yum update -y && \
    yum install -y python38 python38-wheel procps psmisc

# Setup container default configs and directories

WORKDIR /anchore-engine

# Perform OS setup

RUN set -ex && \
    groupadd --gid 1000 anchore && \
    useradd --uid 1000 --gid anchore --shell /bin/bash --create-home anchore && \
    mkdir /config && \
    mkdir /licenses && \
    mkdir -p /workspace_preload /var/log/anchore /var/run/anchore /analysis_scratch /workspace /anchore_service ${NEXTLINUX_SERVICE_DIR} /home/anchore/clamav/db && \
    cp /build_output/LICENSE /licenses/ && \
    cp /build_output/configs/default_config.yaml /config/config.yaml && \
    cp /build_output/configs/docker-entrypoint.sh /docker-entrypoint.sh && \
    cp /build_output/configs/clamav/freshclam.conf /home/anchore/clamav/ && \
    chown -R 1000:0 /workspace_preload /var/log/anchore /var/run/anchore /analysis_scratch /workspace /anchore_service ${NEXTLINUX_SERVICE_DIR} /home/anchore && \
    chmod -R g+rwX /workspace_preload /var/log/anchore /var/run/anchore /analysis_scratch /workspace /anchore_service ${NEXTLINUX_SERVICE_DIR} /home/anchore && \
    chmod -R ug+rw /home/anchore/clamav && \
    md5sum /config/config.yaml > /config/build_installed && \
    chmod +x /docker-entrypoint.sh


# Perform any base OS specific setup

# Perform the anchore-engine build and install

RUN set -ex && \
    pip3 install --no-index --find-links=./ /build_output/wheels/*.whl && \
    cp /build_output/deps/skopeo /usr/bin/skopeo && \
    mkdir -p /etc/containers && \
    cp /build_output/configs/skopeo-policy.json /etc/containers/policy.json && \
    yum install -y /build_output/deps/*.rpm && \
    rm -rf /build_output /root/.cache

# Container runtime instructions

HEALTHCHECK --start-period=20s \
    CMD curl -f http://localhost:8228/health || exit 1

USER 1000

ENV PATH="/anchore_engine/bin:${PATH}"
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["anchore-manager", "service", "start", "--all"]
