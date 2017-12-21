# Sawtooth Marketplace

_Sawtooth Marketplace_ is a blockchain application built on Hyperledger
Sawtooth, allowing users to exchange quantities of customized "Assets" with
other users on the blockchain. This repo contains a number of components which
together with a _Hyperledger Sawtooth_ validator, will run a Sawtooth
blockchain and provide a simple RESTful API to interact with it. The components
in this repo include:

- a **rest api** which provides HTTP/JSON endpoints for querying blockchain data
- a **transaction processor** which handles Marketplace transaction logic
- a **ledger sync** which writes blockchain state changes to a local database
- **SawbuckManager** and an example client which uses Marketplace to create a
  loyalty point program that users can interact with through a simple web app
- a **shell** with all of the dependencies necessary to run support scripts

## Usage

This project utilizes [Docker](https://www.docker.com/what-docker) to simplify
dependencies and deployment. After cloning this repo, follow the instructions
specific to your OS to install and run whatever components are required to run
`docker` and `docker-compose` from your command line. This is only dependency
required to run Marketplace components.

Before startup, the REST API requires a configuration file to be created at
`rest_api/config.py` with sensitive security information and other settings.
An example file is provided to illustrate what settings are available and how
they should be used. To get started, you could simply copy this file into the
appropriate location. Using `bash` from the root project directory, that would
look like this:

```bash
cp rest_api/config.py.example rest_api/config.py
```

Note that while this is fine for development purposes, the example secret keys
provided are _not_ secure. These settings in particular should be changed
before deployment.

Now with your config file in place, Docker can take care of the rest. From the
root project directory, simply run:

```bash
docker-compose up
```

This will take awhile the first time it runs, but when complete will be running
all required components in separate containers. Many of the components will be
available through HTTP endpoints, including:
- The Marketplace REST API will be at **http://localhost:8040**
- The _SawbuckManager_ web app will be at **http://localhost:8041**.
- RethinkDB's admin panel will be available at **http://localhost:8042**
- Sawtooth's blockchain REST API will be available at **http://localhost:8043**

### The Admin CLI

In addition to simply running the components, you will likely want to use the
`mktadm` CLI, which provides commands for interacting with _SawbuckManager_,
like seeding initial data, or scheduling daily deals. This is simple using the
provided shell container. Open a new terminal and run:

```bash
docker exec -it market-shell bash
```

This will open a bash terminal within the shell container, with the `bin/`
directory in the PATH, and all dependencies installed. Now to seed
_SawbuckManager_ with all the needed Offers and Assets run:

```bash
mktadm seed --url market-rest-api:8000 --data sawbuck_app/app_data.yaml
```

And if you would like to schedule daily deals using _cron_, run:

```bash
mktadm schedule --daily "renew --url market-rest-api:8000 --data sawbuck_app/app_data.yaml"
```

Note that you _must_ leave this container running for it to submit new deals
each day. If you just want to  exit the shell (this will not stop the
container), you can simply run:

```bash
exit
```

## Development

The default Docker containers use the `volumes` command to link directly to the
source code on your local machine. As a result any changes you make will
immediately be reflected in the Marketplace components without having to
rebuild them. However, typically you _will_ have to restart a component before
it can take advantage of any changes. This can be done from separate terminal
than the one running your docker containers, using docker and the container
name. For example:

```bash
docker container restart market-rest-api
```

The available container names include:
- market-shell
- market-processor
- market-rest-api
- market-ledger-sync
- market-sawbuck-app
- rethink-db
- sawtooth-shell
- sawtooth-rest-api
- sawtooth-settings-tp
- sawtooth-validator

You can also shutdown _every_ container from the terminal running your
containers. In bash this is typically done by pressing the key combination:
`ctrl-C`. Once shutdown is complete you can restart them (without rebuilding
them), by re-running docker compose up:

```bash
docker-compose up
```

If you want to rebuild the containers (but not the images), before running up,
run down first:

```bash
docker-compose down
```

This will destroy the containers, including any app data that has been saved,
and build them fresh from the original images. This will allow you to start
with a clean slate, but _do not run down_ if you wish to retain your app data.

### Static Client Files and Protobufs

In addition to the above commands, some source code is used to generate
run-time code, and this run-time code will have to be re-generated for changes
to be reflected. The happens automatically anytime you run `up`, but this can
be time consuming if you are rapidly iterating on the code. Dev scripts are
provided to to quickly do this code generation in a temporary docker container
(note that these commands require _bash_).

To generate Protobuf files:

```bash
bin/dev-tools -p
```

To generate static client files:

```bash
bin/dev-tools -c
```

You can also run these scripts directly using the same market-shell container
used to run `mktadm` above. This can be useful if you are on a Windows machine
without access to a bash terminal, or simply want to save yourself the 5-10
seconds required to build and tear down a temporary docker container. First, if
you haven't already, `exec` into the shell:

```bash
docker exec -it market-shell bash
```

Then run the command to generate Protobuf files:

```bash
market-protogen
```

Or the command to generate static client files:

```bash
cd sawbuck_app/
npm run build
```

Note that the static server running _SawbuckManager_ serves the generated
client files directly from your local machine on each page load. This means you
only need to generate the files and refresh your browser to see changes. You do
_not_ need to restart the _SawbuckManager_ container.

## Deployment

Dockerfiles are also available to build images suitable for deployment, and are
demarcated with a `-installed` tag. These will include the source code in the
image itself, rather than referencing what is on your local machine at runtime.
This may be useful if you wish to distribute self-contained docker images which
do not need the source code to run. They can be built individually using the
`docker build` command, or all built and run together using `docker-compose`:

```bash
docker-compose -f docker-compose-installed.yaml up
```

Remember that unlike the default Docker images, if the repo changes, those
changes will not be reflected unless the images are rebuilt. To do that with
`docker-compose`, use:

```bash
docker-compose -f docker-compose-installed.yaml up --build
```

Note that this compose file only exposes the URL for _SawbuckManager_ and the
Marketplace REST API, not Sawtooth or RethinkDB.

## Testing

Docker based integration tests are available. They can be built and run in one
command:

```bash
bin/market-integration-tests
```

By default this command will run all tests in the `integration_tests/`
directory. It is also possible to run a single set of tests by specifying its
sub-directory:

```bash
bin/market-integration-tests rest_api
```

You can also _lint_ your Python code within a docker container using the
`dev-tools` script:

```bash
bin/dev-tools -l
```

## License

Hyperledger Sawtooth software is licensed under the
[Apache License Version 2.0](LICENSE) software license.
