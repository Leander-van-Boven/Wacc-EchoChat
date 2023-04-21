# WaCC chat app EchoChat API

## Quickstart

Everything is dockerized, so it's just a matter of running the container from the root directory of the project.

```shell
docker compose build  # When running the first time
docker compose up WaCC.API.Development [-d]
```

> Bear in mind that this container depends on the `WaCC.DB.Neo4j`, `WaCC.DB.Redis` and `WaCC.DB.Elassandra` containers. If you want to run the API container in isolation, you'll have to run those containers first.

## Deployment

Refer to `deploy.sh` in the `deployment` folder.

## Testing

Build the `Testing.dockerfile` image:
```shell
docker build -t leandervboven/echochat:api-testing -f Testing.dockerfile .
````


and run it like the production image:
```shell
docker run -d -p 8080:8080 \
           -e TESTING=true \
           -e PORT=8080 \
           -e JWT_KEY=$(openssl rand -base64 32) \
           --name api-test \
           leandervboven/echochat:api-testing
```

Then execute:

```shell
docker exec api-test pytest tests
```
