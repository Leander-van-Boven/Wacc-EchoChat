# WaCC chat app EchoChat frontend

## Quickstart

Everything is dockerized, so it's just a matter of running the container from the root directory of the project.

```shell
docker compose build  # When running the first time
docker compose up WaCC.Frontend.Development [-d]
```

> Bear in mind that this container depends on the `WaCC.API.Development` container if you want to do anything that requires interaction with the backend. If you want to run the frontend container in isolation, you'll have to run that container first.

## Deployment

Refer to `deploy.sh` in the `deployment` folder.
