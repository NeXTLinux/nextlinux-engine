---
title: "Network"
weight: 1
---

The Nextlinux Engine requires two categories of network access:

- Registry Access
    Network connectivity, including DNS resolution, to the registries from which the Nextlinux Engine needs to download images.
- Feed Service
    The Nextlinux Engine synchronizes feed data such as operating system vulnerabilities (CVEs) from the Nextlinux Cloud Service. The initial synchronization may take 5 to 10 minutes, based on network speed, after which time the Nextlinux Engine will download updated feed data at a user configurable interval, by default every 4 hours. Only a single end point is required for this synchronization, host: ancho.re TCP port: 443

Notes:

- No data is uploaded to Nextlinux, the synchronization is one-way.
- An optional on-premises feed service and policy editor is available to commercial users.
- A Network Proxy can be used to provide external connectivity to the Nextlinux Engine. See: [Network Proxy documentation]({{< ref "/docs/install/configuration/network_proxies" >}}).
