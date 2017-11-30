# Sawtooth Marketplace

_Sawtooth Marketplace_ is a blockchain application built on Hyperledger
Sawtooth, allowing users to exchange quantities of customized "Assets" with
other users on the blockchain. This repo contains a number of components which
together with a _Hyperledger Sawtooth_ validator, will run a Sawtooth
blockchain and provide a simple RESTful API to interact with it. The components
in this repo will include:

- a **rest api** which provides a REST API for querying blockchain data
- a **transaction processor** which handles RBAC-specific transaction logic
- a **ledger sync** which writes blockchain state changes to a local database
- and an example **client** which uses Marketplace to create a loyalty point
  program administered through a simple web app.

## Usage

The easiest way to run these components is with
[Docker](https://www.docker.com/what-docker). To start these components,
first install Docker for your platform and clone this repo.

Then, generate Python versions of the Protobuf files for each component. From
the sawtooth-marketplace directory:

```bash
bin/dev-tools -p
```

Finally, use `docker-compose` to build and run each component:

```bash
docker-compose up
```

This will create containers for all components with access to the local repo,
and run them along with the necessary Sawtooth components. Once the process is
complete a number of HTTP endpoints will be available:
- The Marketplace REST API will be at **http://localhost:8000**.
- Sawtooth's blockchain REST API will be available at **http://localhost:8008**
- RethinkDB's admin panel will be available at **http://localhost:9090**

Note that some dependencies may need to be installed locally, including
Sawtooth dependencies like the`sawtooth_sdk`, as well as some `pip3` modules.

## Deployment

Dockerfiles are also available to build images suitable for deployment, and are
demarcated with a `-installed` tag. These will build the Protobufs and copy
repo files at build time rather than referencing them locally. They can all be
built individually, or built and run using `docker-compose`:

```bash
docker-compose -f docker-compose-installed.yaml up
```

Unlike the default Docker images, if the repo changes, those changes will not be
reflected unless you rebuild them. To do that with `docker-compose`, use:

```bash
docker-compose -f docker-compose-installed.yaml up --build
```

Note that this compose file only exposes the URL for the Marketplace REST API,
not Sawtooth or RethinkDB.

## License

Hyperledger Sawtooth software is licensed under the
[Apache License Version 2.0](LICENSE) software license.
