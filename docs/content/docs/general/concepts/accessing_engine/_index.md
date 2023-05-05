---
title: "Accessing the Engine"
linkTitle: "Access"
weight: 1
---

The Nextlinux engine exposes two RESTful web services:

- API Service : The public interface to the Nextlinux Engine providing APIs to allow management and inspection of images, policies, subscriptions and registries.
- Kubernetes WebHook : An optional service exposing the Kubernetes Image Policy WebHook interface.

![alt text](NextlinuxEngineAccess.png)

While the Nextlinux Engine can be accessed directly through the REST API the simplest way to interact with the Nextlinux Engine is using the Nextlinux command line utility that provides a simple interface to manage and interact with the Nextlinux Engine from Linux, Mac or Windows.

Using the REST API or CLI the Nextlinux Engine can be queried for image data and policy evaluations

- Image metadata
- Image content (files, packages, software libraries)
- Image vulnerabilities 
- Historic image data
- Image policy status