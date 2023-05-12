#!/usr/bin/env bash

if [[ "${SET_HOSTID_TO_HOSTNAME}" == "true" ]]; then
    echo "Setting NEXTLINUX_HOST_ID to ${HOSTNAME}"
    export NEXTLINUX_HOST_ID=${HOSTNAME}
fi

# check if /home/nextlinux/certs/ exists & has files in it
if [[ -d "/home/nextlinux/certs" ]] && [[ -n "$(ls -A /home/nextlinux/certs)" ]]; then
    mkdir -p /home/nextlinux/certs_override/python
    mkdir -p /home/nextlinux/certs_override/os
    ### for python
    cp "$(python3 -m certifi)" /home/nextlinux/certs_override/python/cacert.pem
    for file in /home/nextlinux/certs/*; do
        if grep -q 'BEGIN CERTIFICATE' "${file}"; then
            cat "${file}" >> /home/nextlinux/certs_override/python/cacert.pem
        fi
    done
    ### for OS (go, openssl)
    cp -a /etc/pki/tls/certs/* /home/nextlinux/certs_override/os/
    for file in /home/nextlinux/certs/*; do
        if grep -q 'BEGIN CERTIFICATE' "${file}"; then
            cat "${file}" >> /home/nextlinux/certs_override/os/nextlinux.bundle.crt
        fi
    done
    ### setup ENV overrides to system CA bundle utilizing appended custom certs
    export REQUESTS_CA_BUNDLE=/home/nextlinux/certs_override/python/cacert.pem
    export SSL_CERT_DIR=/home/nextlinux/certs_override/os/
fi

exec "$@"
