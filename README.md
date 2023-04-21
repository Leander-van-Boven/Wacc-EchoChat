# WaCC chat app EchoChat

This repo consists of all the files that compose a deliverable for the 'Chat app' project for the Web and Cloud Computing course at the University of Groningen.

## Table of contents
- [Quick start](#quick-start)
- [Repo layout](#repo-layout)
- [Architecture](#architecture)
- [Deployment](#deployment)
- [Features](#features)

The Quick start is useful for getting started with the project. The Repo layout, Architecture, Deployment and
 Features sections are useful for understanding the project.

## Quick start

### Local development

Just run the containers.

```shell
docker compose up [-d]
```

#### Containers

- `WaCC.Frontend.Development` - the frontend development container (Vue app)
- `WaCC.API.Development` - the backend development container (REST API using FastAPI (Python))
- `WaCC.DB.Neo4j` - the Neo4j database container (Graph database)
- `WaCC.DB.Elassandra` - Cassandra + Elasticsearch container [more information](https://www.elassandra.io/)
- `WaCC.Redis` - the Redis container (In-memory data structure store, a.o. used as a message broker)

> Note: the API container contains a [wait script](https://github.com/ufoscout/docker-compose-wait) that will wait for the Neo4j, Elassandra and Redis containers to be ready before starting the API server.

### Local deployment

#### Requirements

* [Minikube](https://minikube.sigs.k8s.io/docs/start/)
* [Kubectl](https://kubernetes.io/docs/tasks/tools/)
* [Helm](https://helm.sh/docs/intro/install/)
* Helm charts:
  ```
  helm repo add neo4j https://helm.neo4j.com/neo4j
  helm repo add bitnami https://charts.bitnami.com/bitnami
  helm repo add grafana https://grafana.github.io/helm-charts
  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

  helm repo update
  ```

#### Steps

First run minikube, preferably with as many resources as possible:
```sh
minikube start --cpus=max --memory=max
```

This should set `kubectl` to connect to the minikube cluster running.

Then the different namespaces and secrets should be created:
```sh
kubectl create -f ./deployment/kubernetes/namespaces.yaml
kubectl create -f ./deployment/kubernetes/secrets.yaml
```

After these steps, the different services can be deployed:
```sh
# Elassandra
kubectl apply -f ./elassandra/deployment/service.yaml
kubectl apply -f ./elassandra/deployment/statefulset.yaml

# Neo4J
helm install --namespace echochat-databases neo4j-core-0 neo4j/neo4j-cluster-core -f ./neo4j/deployment/core-values.yaml
helm install --namespace echochat-databases neo4j-core-1 neo4j/neo4j-cluster-core -f ./neo4j/deployment/core-values.yaml
helm install --namespace echochat-databases neo4j-core-2 neo4j/neo4j-cluster-core -f ./neo4j/deployment/core-values.yaml

helm install --namespace echochat-databases neo4j-headless neo4j/neo4j-cluster-headless-service --set neo4j.name=echochat-neo4j-cluster

# Redis
helm install --namespace echochat-databases redis bitnami/redis

# Loki
helm upgrade --install loki grafana/loki-simple-scalable \
  --namespace echochat-monitoring \
  --set loki.auth_enabled=false

# Promtail
helm upgrade --install promtail grafana/promtail \
  --namespace echochat-monitoring \
  --set loki.serviceName=loki-gateway

# Grafana
helm upgrade --install grafana grafana/grafana \
  --namespace echochat-monitoring \
  --set persistence.enabled=true \
  --set persistence.size=5Gi \
  --set persistence.storageClassName=local-path \
  --set adminPassword=grafana

# Tempo
helm upgrade --install tempo grafana/tempo \
  --namespace echochat-monitoring

# Prometheus
helm upgrade --install prometheus prometheus-community/prometheus \
  --namespace echochat-monitoring \
  --set alertmanager.enabled=false \
  --set server.persistentVolume.storageClass=local-path

# API
kubectl apply -f ./api/deployment/service.yaml
kubectl apply -f ./api/deployment/secrets.yaml
kubectl apply -f ./api/deployment/deployment.yaml

# Frontend
kubectl apply -f ./frontend/deployment/service.yaml
kubectl apply -f ./frontend/deployment/deployment.yaml
kubectl apply -f ./frontend/deployment/ingress.yaml
```

### Production deployment
Production deployment follows the same steps as local deployment, however most services don't require an continuous deployment. The services that do (Frontend and API) are continuously deployed on pushes to the `main` and `development` branches by CI/CD (GitHub Actions), more information in the deployment sections for the [frontend](#frontend-1) and [backend](#backend-1) respectively.

## Repo layout

Refer to below for a quick overview of the repo layout, in terms of its high level folders.

```
.
├── api                  # Root folder of the backend API  
│   ├── app              # Contains the API source code
│   ├── deployment       # Contains Kubernetes manifests for deploying the API
│   └── tests            # API tests for the FastAPI app
│
├── architecture         # Contains initial presentation about the architecture
│
├── deployment           # Contains folders and files that are related to deployment
│   ├── flatcar          # Contains files for building a Flatcar image with K3S on OpenStack
│   ├── k8s.dashboard    # Contains files for deploying the Kubernetes dashboard
│   ├── kubernetes       # Contains Kubernetes manifest files for initial cluster setup
│   └── _templates       # templates found online that might be usefull
│
├── docker-compose.yaml  # docker-compose file for local development
│
├── elassandra           # Root folder for Elassandra
│   └── deployment       # Contains Kubernetes manifests for deploying Elassandra
│
├── frontend             # Root folder of the frontend
│   ├── deployment       # Contains Kubernetes manifests for deploying the frontend
│   └── src              # Contains the frontend source code
│
├── grafana              # Root folder for Grafana
│   └── deployment       # Helm chart scripts for deploying Grafana, Loki, Promtail and Tempo
│
├── neo4j                # Root folder for Neo4j
│   └── deployment       # Contains Helm chart settings for deploying Neo4j
│
├── prometheus           # Root folder for Prometheus
│   └── deployment       # Helm chart scripts for deploying Prometheus
│
├── README.md            # This README
│
├── redis                # Root folder for Redis
│   └── deployment       # Helm chart scripts for deploying Redis
│
└── sentry               # [NOT USED] Root folder for Sentry
    └── deployment       # [NOT USED] Helm chart scripts for deploying Sentry
```

## Architecture

As can be seen from the container services layout in the [Docker compose file](docker-compose.yaml), the architecture is split into 4 main parts:

- [A frontend](#frontend) accessible through by the end-user via a web browser;
- [the backend / api](#backend) that handles the communication between the frontend and the databases;
- [the databases](#databases) that store the data;
- and [monitoring](#monitoring) that provides insight into the health of, and statistics about the system.

Every service is dockerized to allow for development in a production-like environment. The services are orchestrated using [docker-compose](https://docs.docker.com/compose/), which allows for easy deployment of the services on a local machine. As all services are connected to the same docker network, they can communicate with each other using their service name as hostname.

### Frontend
The frontend is written in Javascript making use of the [Vue Javascript Framework](https://vuejs.org/). It is a single page application that communicates with the backend via HTTP requests and through websockets.

The framework was preferred over a more traditional way of implementing an SPA using JQuery as Vue offers the ability to bundle the project into a smaller package more suitable for browsers, a development server that auto-reloads the page on changes and Quality-of-Life features such as a component system, routers and support for more advanced packages.

Especially this last feature was utilised, as there exists an NPM package called [vue-advanced-chat](https://www.npmjs.com/package/vue-advanced-chat) that provides a chat component that is very similar to the one that was required for this project. This package was used as a starting point for the frontend, and was extended to fit the requirements of the project. The basic features of this package include a decent styled chat component that exposes properties such as `rooms` and `messages` that have to be set and updated by the implementer as well as events such as `fetch-messages`, `fetch-more-rooms` and `send-message` that need to be handled by the implementer.

For basic interaction and CRUD operations with the backend, [Axios](https://github.com/axios/axios) was used to perform Promise-based RESTful HTTP requests as it is one of the most popular packages regarding this functionality. However, as the backend should also be able to push newly received messages to the frontend, websockets were implemented as well, using the build in `WebSocket` class as no extensive features were required.

On top of the chat view, a login view and an admin page were added. The former is used to differentiate between different end-users using the chat application by means of JSON-Web-Tokens (JWT), making it possible to scope messages to a specific user. The latter is used to display the current status of the system, such as the number of users and rooms, and the number of messages that have been sent (this feature is not yet available at the time of typing this, but is on the roadmap).

In order to make the app more maintainable, all backend interaction functions are abstracted into their own files, allowing them to be easily replaced if necessary, without having to change the function calls in the components that consume them. Furthermore, this allows the functions to be wrapped in `try/catch` blocks, which allows for error handling to be done in a single place, making the app more robust.

Numerous additional features were implemented as well, please refer to the [extra features](#extra-features) section for more information.


### Backend
The backend is written in Python using FastAPI. Python was chosen as the main language for the backend service as it is one of the most popular backend languages, easy to learn and has a lot of third party packages available for e.g. database integrations. FastAPI was chosen as the API framework, over e.g. Flask or Django, as it is a modern, well-maintained fully asynchronous framework that is easy to use and has a lot of features that are useful for this project, such as automatic documentation generation, a built-in webserver and decorator based endpoint specifications enhanced by [Pydantic](https://pydantic-docs.helpmanual.io/) for type validation. 

The backend is split into 3 main parts:
- the models;
- the schemas;
- and the routers.

The models specify object relational mappings (ORM) for the database tables, allowing for easy CRUD operations on the databases. The databases used in question are [Elassandra](#elassandra) (e.g. Cassandra + Elasticsearch) and [Neo4j](#neo4j) (graph database). Refer to the [databases](#databases) section for more information on these databases and why they were chosen for which models.

The schemas specify the data that is expected to be received by the backend, and the data that is returned by the backend. Pydantic in combination with Python build-in typing system allows for automatic type validation of the data, in either direction. Id est, if the backend receives data that does not match the schema, it will automatically return a [400 HTTP response](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400) (Bad Request). If the backend returns data that does not match the schema, the frontend will not be able to handle it, and therefore a [500 HTTP response](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500) (Internal Server Error) will be returned.

The routers specify the endpoints that are exposed by the backend, and the functions that are called when a request is made to these endpoints. This ranges from simple CRUD operations to more complex operations such as sending messages to other users.

Each of these three parts are on their own subdivided into the different models that are used in the backend. This allows for easy maintenance of the backend, as each model will have its respective file in the `models`, `schemas` and `routers` folders respectively. Furthermore, this allows for easy extension of the backend, as new models can be added without having to change the existing code.

Additional integrations were implemented on top of the database integrations. These integrations include:
- `fastapi-distributed-websockets`, this package allows us in combination with [Redis](#redis) as a broker to send websocket message from any backend node to the correct client.
- Elasticsearch search functionality (elaborated further in the [Elassandra](#elassandra) section);
- monitoring of the system (elaborated further in the [monitoring](#monitoring) section);
- and a JWT authentication system (elaborated further in the [authentication](#authentication) section).

Also, here additional smaller, but very useful, features were implemented, they can be found in the [extra features](#extra-features) section.

### Databases
We chose to deploy two different kinds of NoSQL databases to exploit the different strengths of each database. We chose to use Cassandra and Neo4j.

#### Elassandra
Cassandra was chosen due to its recognized ability to handle time series data very efficiently. This is important for (popular) chat applications, as they will see a lot of traffic of data that can best be represented as time series data.

Hence, it was chosen to only save messages in Cassandra, as it would not make sense to save users or chat rooms as that data can be better represented in a graph (refer to the [Neo4j](#neo4j) section for more information on this). To improve performance even further, careful considerations were performed to determine the optimal schema for the message model. This resulted in following schema:
```python
class Message(Model):
    room_id: UUID = columns.UUID(primary_key=True, partition_key=True)
    index_id = columns.DateTime(primary_key=True, clustering_order='ASC')
    uuid: UUID = columns.UUID(primary_key=True)
```
meaning that the room identifier of the message was used as the primary partition key, because we should be able to get all messages for a single chatroom very efficiently. Subsequently, the `index_id` was chosen as the first clustering key, as this is a value exposed by the frontend chat package, which is used to have a persistent sorting of the messages in a chatroom (hence the type of this column is a datetime). By having this clustering key with the specific clustering order (ascending), we can get all messages for a single chatroom in a specific time range very efficiently. Lastly, the `uuid` was chosen as the second clustering key, as this is a unique identifier for each message, allowing us to get a specific message without having to maintain a custom index for that.

We expect this to be quite performant as these keys do not change after a message is created, not requiring any re-indexing.

##### Elasticsearch
By default, it is not possible to do ad-hoc queries in a Cassandra database. This makes it very hard to perform search queries as you miss the freedom to select any field of the message object to filter on. This could be solved by adding an index on any field that might be used for filtering, but this would very likely decrease the performance of the database, making the database less suitable for its primary purpose: storing time series data.

Luckily, this problem was solved by Elastic, who invented Elasticsearch; a very search engine that very efficiently handles its indexes. However, Elasticsearch lacks performance regarding time series data in comparison with Cassandra. Luckily, also this problem was resolved by the invention of Elassandra, which is a combination of Cassandra and Elasticsearch. This allows for the best of both worlds: the performance of Cassandra for time series data, and the search functionality of Elasticsearch. Therefore, this specific 'distribution' of Cassandra was chosen for storing the message objects. Whenever any update is performed in the Cassandra database, the corresponding Elasticsearch index is *eventually* updated as well.

#### Neo4j
Neo4j was chosen as the second (NoSQL) database due to its ability to store relationships between nodes as Neo4j is a graph database. This is important for a chat application, as we want to be able to store the relationships between users as they are formed through chat rooms. We can also create different status nodes for which only one can be connected to a user at a time, making it possible to query for all online users, which in turn will be quite useful for statistics / data science were this an application in a for-profit business.

Hence, we have created three different schemas: the `user`, a `userstatus` and a `room`. A user has two relations, one to a user status and a many-to-many relation with the rooms. The user status relation has an additional property called `last_changed` used to keep track of the last time the user status was changed. The room relation has an additional property called `is_typing` used to keep track of whether a user is typing in a specific room. This is used to show a typing indicator in the chat room. In theory one could also add an extra property to this relation called `last_message` to keep track of the last message that this specific user send in the chatroom. However, this would require a lot of extra work to keep this property up to date, as it would require a lot of extra queries to the Cassandra database, that can also be done while querying the Cassandra database for the messages. Therefore, this was not implemented.

#### Redis

Redis was deployed as a part of the websocket implementation. This was done, as without it, it would be possible for two clients that want to chat in the same chatroom to connect to different backend nodes. However, each backend node is not aware of the websocket connections on the other backend node, and hence it will not be possible to forward a message from one client to the other. This is solved by using Redis as a broker, which is a central point of communication between the backend nodes.

Each backend node has a Redis consumer and publisher. The consumer waits for any websocket message that is destined for an active websocket connection on that specific backend node (based on the `topic` of the websocket message). The publisher publishes any websocket message that is destined for an active websocket connection on another backend node (based on the `topic` of the websocket message). This allows for the backend nodes to communicate with each other, and hence for the backend nodes to be able to send messages to each other.

## Deployment

As each service can be run as a docker container, they can also be deployed on Kubernetes as such. Refer below to the decisions / setup of the actual deployment of each service. As each service is its own deployment, it is possible to scale each service independently, but also fault tolerance is achieved as each service can be deployed on multiple nodes, and Kubernetes will automatically restart a service if it crashes. 

### Kubernetes

However before a service can be deployed on Kubernetes, Kubernetes itself had to be deployed.

We were provided with a bare-metal OpenStack cluster. We used Terraform to define a basic setup of a K3s cluster with 1 master and 2 slave nodes running on Flatcar OS virtual machines on the OpenStack cluster. Only the master node has an outside connection using an allocated floating IP from an external vlan floating IP pool connected through a router. The `Traefik` ingress controller shipped with K3s provides load balancing of requests to the master and slave node services. 

We are aware that this setup creates a single-point-of-failure, however resolving this would require a far more complex setup, which regarding the time and resource constraints of this project (in combination with Merlin HPC outages), was not feasible.

> In terms of a time spent on a single 'feature', this part of the project took by far the most amount of time.

#### Kubernetes dashboard

To make the cluster more accessible, we deployed the [Kubernetes dashboard](https://github.com/kubernetes/dashboard) to view and update the resources in the different namespaces, in combination with the metrics plugin to view the amount of resources used by each service. 


### Frontend

During development, the code is build and served by the `npm` package manager inside a `node:lts-alpine` container. However, this is not suitable for production. Therefore, the frontend is build (making the source code smaller by removal of comments, docstrings and obfuscation) and served by the `nginx` web server inside a `nginx:stable-alpine` container using a multistage build process. This container is configured to serve the static files that are generated by the build process. This container is also configured to serve the `index.html` file for all requests that are not for a static file. This is done to allow for the frontend to handle routing, as the frontend is a single page application.

The frontend is deployed on a Kubernetes cluster using the `Treafik` ingress controller, shipped with K3s. This controller is configured to route all requests to the frontend to the frontend `Service`. This also allows for load balancing. This service is configured to route all requests, that are not prefixed with `/api`, to the frontend pods. These pods are deployed using a `Deployment` as we don't require any stateful data to be stored on the frontend. A `HorizontalPodAutoscaler` is also configured to scale the frontend pods based on the CPU and memory usage of the pods. This is done to ensure that the frontend is always available, even when the traffic increases.

These resources are configured using raw Kubernetes manifest files, as no additional configuration is required, making a Helm chart unnecessary.

#### CI/CD

As the frontend will be continuously developed, on each push to either the `main` or `development` branch, a pipeline is triggered that first builds the production docker image and pushes it to Dockerhub, then a secondary job is triggered that will perform a rolling update of the frontend pods (`kubectl rollout restart`). This is done to ensure that the frontend is always available, even during the upgrade. This pipeline makes use of the GitHub Actions Cache to make the build process faster.


### Backend

The backend contains three different Dockerfiles, as each is tailored towards specific purposes. The `Development.dockerfile` runs the application with auto-reload enabled and has the `fastapi-distributed-websockets` packages installed as [editable](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-e). This allows to make changes to the code and have them automatically be reflected in the running application. This is useful for development, but not for production. Therefore, the `Production.dockerfile` is used to build the application for production. This Dockerfile does not install the `fastapi-distributed-websockets` package as editable, but instead installs it as a normal package instead. This Dockerfile also does not run the application with auto-reload enabled and on port 80 by default. This is done to ensure that the application is as performant as possible. The `Production.dockerfile` is also used as base to build the application for testing. This is done to ensure that the application is tested in the same environment as it is deployed in. However, the `Testing.dockerfile` will also copy the test files into the container and install the additional packages required for testing.

The production image is deployed inside a `Deployment`, with a `HorizontalPodAutoscaler` to automatically increase the number of pods when the CPU or memory usage increases. Once again, the `Traefik` ingress controller is used to handle ingress and route requests prefixed with `/api` to the backend `Service`. Additionally `Secrets` were deployed to store the database credentials and the JWT secret. These secrets are mounted as environment variables inside the pods. This is done to ensure that the credentials are not stored in plain text inside the pods.

Also the backend is deployed using raw Kubernetes manifest files.

#### CI/CD

As also the backend will be continuously developed, on each push to either the `main` or `development` branch, a pipeline is triggered that first builds the production docker image and pushes it to Dockerhub, then a secondary job is triggered that will build the testing image and run the tests. Whenever the tests are successful, a third job is started that will perform the rolling upgrade on the backend deployment. Once again, the GitHub Actions cache is used to make the build process faster.


### Databases

#### Neo4j

The developers of Neo4j have provided Helm charts to deploy a cluster onto Kubernetes with minor configuration required. Hence, this method of deploying Neo4j was used.

To be highly available, this version of the Neo4j deployment requires 3 master (or core as they call them) nodes, that allow both reads and writes, to be deployed before the Neo4j cluster will be available. Finally, a headless service can be deployed to load balance traffic between the different master nodes. Additionally, read nodes can be deployed as well, but due to constraints in the amount of available server resources, and the low amount of traffic, this was not done.

#### Elassandra

Elassandra does not come with a Helm chart, but the developers have provided example Kubernetes manifests, so these were deployed instead. Currently, the Elassandra cluster is deployed with a single node, as the amount of traffic is low and a second node on either of the Kubernetes slave nodes would have enough RAM allocated.

Elassandra is deployed using a `StatefulSet`, with a `Service`.

#### Redis

Redis was deployed using the official Helm chart provided by Bitnami. This deployed a single master node with three read replicas.

### Monitoring

On top of the metrics provided by the Kubernetes dashboard metrics plugin, we also wanted to be able to gain metrics from the API service in particular. To this end a number of extra services were deployed, that can also be connected to monitor other services.

#### Sentry

The first way of monitoring is performed through [Sentry](https://sentry.io/). Sentry is a service that allows for monitoring of errors and exceptions that occur in the application. This is done by sending the errors to Sentry, which will then display them in a dashboard. This allows for easy debugging of errors and exceptions that occur in the production application, and are otherwise not as easily detected.

Sentry was integrated into the API using the `sentry-sdk` package with the `fastapi` extra. For this project the SaaS version of Sentry was used, but it is also possible to host Sentry yourself.

#### Prometheus

The second way of monitoring is performed through [Prometheus](https://prometheus.io/). Prometheus is a monitoring system that scrapes metrics from different sources and stores them in a time series database. This allows for easy querying of the metrics, and allows for easy creation of dashboards. Prometheus is also able to alert when certain metrics are above or below a certain threshold, though this feature is not used in this project. Prometheus is also able to scrape metrics from the Kubernetes API, which allows for monitoring of the Kubernetes cluster itself too. The data from Prometheus can then be visualized in a [Grafana dashboard](#grafana).

Prometheus was deployed using community Helm charts, and then configured to scrape the metrics from the API service. To this end, the `prometheus-client` package was installed, and an extra endpoint was added to the API service that exposes the metrics in the Prometheus format. This endpoint is only available in production, as it is not needed in development.

#### Grafana

[Grafana](https://grafana.com/) is a visualization tool that allows for easy creation of dashboards. Grafana can be connected to a variety of data sources that act as the source of the data for the different dashboards. 

An existing Grafana dashboard was modified to fit the needs of this project.

Grafana was deployed using the Helm charts provided by Grafana. Then the individual data sources were added (Prometheus, Loki and Tempo).

#### Loki

[Loki](https://grafana.com/oss/loki/) is a log aggregation system that is used to store logs from the API service. This allows for obtaining information about certain actions that happen in the API but are not logged as errors to Sentry.

Loki was deployed using the Helm charts provided by Grafana.

#### Tempo

[Tempo](https://grafana.com/oss/tempo/) is a distributed tracing system that is used to trace the requests that are made to the API service. This allows for obtaining performance information about the API service, such as the time it takes for a request to be processed, and which parts of the code are executed during the processing of the request.

Tempo was deployed using the Helm charts provided by Grafana. Then the `opentelemetry` package was added to the API service and a `FastAPIInstrumentor` was initialised that sends the traces to Tempo.


#### Promtail

[Promtail](https://grafana.com/oss/promtail/) is a log agent, that is quite crucial for the monitoring as it is used to send the logs from all services that are running in the Kubernetes cluster to Loki. This allows for obtaining information about the logs of all services that are running in the Kubernetes cluster, thereby allowing to make Grafana dashboards for it.

## Features

In addition to the practical setup of the project, an number of features were implemented to showcase the capabilities of the project.

### Fault tolerance
The project is designed to be fault tolerant. This means that if a service goes down, the other services will continue to function. This is done by using a number of different techniques.

The frontend employs a Promise-then-catch pattern to handle errors. This means that if a request to the backend fails, the frontend will display an error message to the user, but will not crash.

By default, the backend performs any request within its own scope. This means that, whenever a request to the backend fails, a HTTP 500 error is returned rather than crashing the backend service. Any websocket action that encounters an error, will close the websocket connection, instead of crashing the service. However, some circumstances will still be able to crash the backend, therefore these parts have been put in `try`-`except` blocks.

Additional efforts have been put into making the frontend and backend services **recover** from a crash, without having to restart the service. To this end, utility functions will periodically check the connection to the various databases, and will attempt to reconnect if the connection is lost.

If, by any chance (no code-base is perfect), the backend service does crash, the Kubernetes deployment will automatically restart the service, and the service ~~should~~ will be available again.


### Authentication
First is a fully state-less authentication system using JSON-Web-Tokens (JWT). On login, a user send its credentials to the API, which then checks the credentials against the database. If the credentials are correct, a JWT is generated and returned to the user. This JWT can then be used to authenticate the user for future requests. This allows for the API to be state-less, as the user does not need to be checked to the databases for each request, but only needs to send the JWT with each request. This JWT is also signed using a secret key, which ensures that the JWT cannot be forged, nor edited, as the JWT will contain an expiry date. This expiry time can be set to any value, however lower values will mean a more secure application, while higher values will give a better user experience as the user will not need to login as often.

### Search
As mentioned in the [databases](#databases) section, Elassandra features Elasticsearch. This allows for the frontend to perform searches on message content, while this not being an index in the Cassandra database.

Right now, the behaviour of the search tries to mimic WhatsApp's search behaviour. This means that the search will return chat rooms matching the search query for the first two characters entered and will then return any message which content matches the search query, and is sent in one of the chat rooms the currently logged-in user is a member of.

### API testing suite

To ensure that the API is working as expected, a testing suite was created. This testing suite is run on each push to the `main` or `development` branch, and will fail if any of the tests fail. This testing suite is written using the `pytest` package, and uses the `requests` package to make requests to the API. [Unittest mocking](https://docs.python.org/3/library/unittest.mock.html) was used to mock any ORM related operation so that no database connection nor a testing database setup is required to perform the tests.

### Message pagination

In order to improve performance and reduce the amount of data that needs to be transferred, the API supports pagination of messages. This means that the frontend can request a certain amount of messages, and then request the next page of messages when the user scrolls to the top of the chat room. This allows for the frontend to only load the messages that are currently visible to the user, and not all messages in the chat room.

This is implemented using a `PreparedStatement` meaning that the actual CQL query is send to the database upon the first time of performing the query. Every subsequent query only requires the `room_id` and `count` parameters to be send to the database, which is much faster than sending, parsing and validating the entire query each time.

### Admin page

Admin page allows one to see the current statistics of the application. Right now, this is fairly limited, however the way it's build allows for very easy expansion. The admin page is only accessible to users with the `admin` role.

For now the only statistic is the amount of users and how many of them are online.

### Extra features

On top of the more elaborate features listed above, the following smaller features were implemented for the respective services.

#### Frontend
- **Browser notifications:** When a user receives a new message, a browser notification is sent to the user.
- **Progressive-Web-App (PWA) support:** allows for the app to be installed as a native app on any device with a web browser.
- **Dark mode**
- **Emoji support**
- **Ability to create, join and leave chat rooms on-demand**
- **Real-time message received and read receipts** (performed using websockets)
- **User real-time status changes** (performed using websockets)

#### Backend
- **Automatic documentation** of the API using Swagger and Redoc
- **Fully documented code** using docstrings and comments
- **Easily extendable** to support more features


## Future work
- **End-to-end encryption using the JWT tokens**. This will be especially hard for chatrooms as users may join and leave.
- **HTTPS support**. This is currently not supported but would be very nice for a real production environment.
- **expand current features**, like real time message distributed, user is typing, etc.

![chat](https://imgs.xkcd.com/comics/encryption.png)
