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

## License

Hyperledger Sawtooth software is licensed under the
[Apache License Version 2.0](LICENSE) software license.
