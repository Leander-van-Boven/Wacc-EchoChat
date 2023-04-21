# Echochat API tests

This directory contains the tests for the Echochat API.
The tests are made for `pytest` and as such, need to be run by `pytest`.

## Running the tests

### Pre-requisites
- Have the Echochat API container running
- Have `pytest` and `requests` and `python-multipart` installed in the container pip environment

### Running the tests
From the `/api` directory, run the following:
```
pytest tests
```