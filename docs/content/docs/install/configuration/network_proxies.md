---
title: "Network Proxies"
linkTitle: "Network Proxies"
weight: 5
---

As covered in the Network sections of the requirements document the Nextlinux Engine requires three categories of network connectivity. 

- Registry Access
  Network connectivity, including DNS resolution, to the registries from which the Nextlinux Engine needs to download images.

- Feed Service
  The Nextlinux Engine synchronizes feed data such as operating system vulnerabilities (CVEs) from the Nextlinux Cloud Service. Only a single end point is required for this synchronization, host: ancho.re TCP port: 443

- Access to Nextlinux Internal Services
  The Nextlinux Engine is comprised of six smaller micro-services that can be deployed in a single container or scaled out to handle load. Each Nextlinux service should be able to connect the other services over the network.

In environments were access to the public internet is restricted then a proxy server may be required to allow the Nextlinux Engine to connect to the Nextlinux Cloud Feed Service or to a publicly hosted container registry.

The Nextlinux Engine can be configured to access a proxy server by using environment variables that are read by the Nextlinux Engine at run time.

- https_proxy:
  Address of the proxy service to use for HTTPS traffic in the following form: {PROTOCOL}://{IP or HOSTNAME}:{PORT}
  eg. https://proxy.corp.example.com:8128

- http_proxy:    
  Address of the proxy service to use for HTTP traffic in the following form: {PROTOCOL}://{IP or HOSTNAME}:{PORT}   
  eg. http://proxy.corp.example.com:8128

- no_proxy:   
  Comma delimited list of hostnames or IP address which should be accessed directly without using the proxy service.
  eg. localhost,127.0.0.1,registry,example.com

### Notes:

- Do not use double quotes (") around the proxy variable values. 

### Authentication

For proxy servers that require authentication the username and password can be provided as part of the URL:

eg. https_proxy=https://user:password@proxy.corp.example.com:8128

If the username or password contains and non-url safe characters then these should be urlencoded.

For example:

`The password F@oBar! would be encoded as F%40oBar%21`

### Setting Environment Variables

Docker Compose: https://docs.docker.com/compose/environment-variables/

Kubernetes: https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/

### Deployment Architecture Notes

When setting up a network proxy, keep in mind that you will need to explicitly allow inter-service communication within the nextlinux engine deployment to bypass the proxy, and potentially other hostnames as well (e.g. internal registries) to ensure that traffic is directed correctly.  In general, all nextlinux engine service endpoints (the URLs for enabled services in the output of an 'nextlinux-cli system status' command) as well as any internal registries (the hostnames you may have set up with 'nextlinux-cli registry add <hostname> ...' or as part of an un-credentialed image add 'nextlinux-cli image add <registry:port>/....'), should not be proxied (i.e. added to the no_proxy list, as described above).

If you wish to tune this further, below is a list of each component that makes an external URL fetch for various purposes:

- catalog: makes connections to image registries (any host added via 'nextlinux-cli registry add' or directly via 'nextlinux-cli image add')
- analyzer: same as catalog
- policy_engine: by default, makes HTTPS connection to https://ancho.re feed service, unless on-prem feed service is deployed