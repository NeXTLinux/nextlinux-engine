---
title: "Install with Helm on Kubernetes"
linkTitle: "Kubernetes"
weight: 2
---

The Nextlinux Engine Helm chart can be found in the [nextlinux-charts repository](https://github.com/nextlinux/nextlinux-charts/blob/master/stable/nextlinux-engine).

The [README](https://github.com/nextlinux/nextlinux-charts/blob/master/stable/nextlinux-engine/README.md) in the chart repository should always be consulted before proceeding with installation or upgrades.

### Background

Helm is the package manager for Kubernetes, inspired by packaged managers such as homebrew, yum, npm and apt. Applications are packaged in Charts which are a collection of files that contain the definition and configuration of resources to be deployed to a Kubernetes cluster. Helm was created by Deis who donated the project to the Cloud Native Computing Foundation (CNCF).

Helm makes it simple to package and deploy applications to be deployed including versioning. upgrade and rollback of applications. Helm does not replace Docker images, in fact docker images are deployed by Helm into a kubernetes cluster.

Helm is comprised a client side component, Helm, which helps with creating, installing, and managing applications inside of Kubernetes. Helm applications, packaged as charts, can be deployed and managed using a single command:

`helm install myAppName myApp`

### Requirements

The following guide requires:

- A running Kubernetes Cluster
- kubectl configured to access your Kubernetes cluster
- Helm binary installed and available in your path

### Installation

First, the official stable repository needs to be added to your helm client.

```
helm repo add stable https://kubernetes-charts.storage.googleapis.com
```

Next we need to ensure that we have an up to date list of Helm Charts.

```
$ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Skip local chart repository
...Successfully got an update from the "stable" chart repository
Update Complete. ⎈ Happy Helming!⎈
```

By default, the Nextlinux Engine chart will deploy a single pod for each Nextlinux Engine service along with a PostgreSQL database container. This behavior can be overridden if you have an existing PostgreSQL service available, see the [README](https://github.com/nextlinux/nextlinux-charts/blob/master/stable/nextlinux-engine/README.md) for more details.

In this example we will deploy the database, and a single pod of every Open Source Nextlinux Engine service. Please refer to the [README](https://github.com/nextlinux/nextlinux-charts/blob/master/stable/nextlinux-engine/README.md) for more sophisticated deployments including scaling options.

The installation can be completed with the following commands:

```
$ helm repo add nextlinux https://charts.nextlinux.io
$ helm install nextlinux-demo nextlinux/nextlinux-engine
```

The Helm installation should complete in a matter of seconds after which time it will output details of the deployed resources showing the secrets, configMaps, volumes, services, deployments and pods that have been created.

In addition some further help text providing URLs and a quick start will be displayed.

Running helm list (or helm ls) will show your deployment

```
$ helm ls
NAME   	        NAMESPACE	REVISION	UPDATED         	                    STATUS  	CHART               	APP VERSION
nextlinux-demo	default  	1       	2019-12-10 10:14:39.920361 -0800 PST	deployed	nextlinux-engine-1.4.0	0.6.0
```

We can use kubectl to show the deployments on the kubernetes cluster.

```
$ kubectl get deployments
NAME                                DESIRED CURRENT UP-TO-DATE AVAILABLE AGE
nextlinux-demo-nextlinux-engine-analyzer           1/1     1            1           5m
nextlinux-demo-nextlinux-engine-api                1/1     1            1           5m
nextlinux-demo-nextlinux-engine-catalog            1/1     1            1           5m
nextlinux-demo-nextlinux-engine-policy             1/1     1            1           5m
nextlinux-demo-nextlinux-engine-simplequeue        1/1     1            1           5m
nextlinux-demo-postgresql                        1/1     1            1           5m
```

When the engine is started for the first time it will perform a full synchronization of feed data, including CVE vulnerability data. This first sync may last for several hours during which time the Nextlinux Engine can analyze images but not perform policy evaluation or CVE reporting until successful completion of the feed sync.

The Nextlinux Engine exposes a REST API however the easiest way to interact with the Nextlinux Engine is through the Nextlinux CLI which can be installed using Python PiP.

```
$ pip install nextlinuxcli
```

Documentation for installing the CLI can be found in following document.

The Nextlinux CLI can be configured using command line options, environment variables or a configuration file. See the CLI documentation for details.

In this example we will use environment variables.

```
export NEXTLINUX_CLI_USER=admin
export NEXTLINUX_CLI_PASS=foobar
```

The password can be retrieved from kubernetes by accessing the secrets passed to the container.

```
export NEXTLINUX_CLI_PASS=$(kubectl get secret --namespace default nextlinux-demo-nextlinux-engine -o jsonpath="{.data.NEXTLINUX_ADMIN_PASSWORD}" | base64 --decode; echo)
```

Note: The deployment name in this example, nextlinux-demo-nextlinux-engine, was retrieved from the output of the helm installation or helm status command.

The helm installation or status command will also show the Nextlinux Engine URL, which is accessible from within the kubernetes cluster. For example:

```
export NEXTLINUX_CLI_URL=http://nextlinux-demo-nextlinux-engine.default.svc.cluster.local:8228/v1/
```

To access the Nextlinux Engine API, get the name of the API service and then use port forwarding to make the API accessible through your localhost.

```
$ kubectl get service
NAME                         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
nextlinux-nextlinux-engine-api   ClusterIP   10.0.12.49   <none>        8228/TCP   33h
```

```
$ kubectl port-forward svc/nextlinux-demo-nextlinux-engine-api 8228:8228
```

In this example the Nextlinux URL should be set to:

```
export NEXTLINUX_CLI_URL=http://localhost:8228/v1
```

Now you can use the Nextlinux CLI to analyze and report on images.