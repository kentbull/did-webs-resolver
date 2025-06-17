# Introduction

A demonstration of a `did:webs` service and resolver. Implements the
`did:webs` [specification](https://trustoverip.github.io/tswg-did-method-webs-specification/).

[![CI](https://github.com/GLEIF-IT/did-webs-resolver/actions/workflows/ci.yml/badge.svg)](https://github.com/GLEIF-IT/did-webs-resolver/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/GLEIF-IT/did-webs-resolver/branch/main/graph/badge.svg?token=sUADtbanWC)](https://codecov.io/gh/GLEIF-IT/did-webs-resolver)

### Developers - Getting Started

Developers who want to jump into using the `did:webs` reference implementation should follow
the [Getting Started](docs/getting_started) guide.

A breakdown of the commands can be found [here](./docs/commands.md).

#### did:webs service

For a `did:webs` service to operate securely it should only sever AIDs whose KELs have been processed into the service's database.

There are two methods to do this:

1. Local only support - start the serivce using an existing local keystore.

This is useful for development and can be done by provide an existing named keystore to the `did:webs` service.

For example, to start the service using the `multisig1` keystore (https://github.com/WebOfTrust/keripy/blob/v1.2.4/scripts/demo/basic/multisig.sh)

```bash
dkr did webs service --name multisig1
```

2. Import supported - start the service using an empty local keystore, and import AID KELs. The following workflow can be applied to start the service, export an existing keystore and import it to the service.

```bash
dkr did webs service --name dkr
```

```bash
kli export --name multisig1 --files 
```

to import an AID to the service securely we use a IPEX Grant to present the exported KEL to the service.

```bash
kli grant 
```


#### Bootstrapping

### Prior art

did:keri resolver by Philip Feairheller @pfeairheller [here](https://github.com/WebOfTrust/did-keri-resolver)

Thank you to Markus Sabadello @peacekeeper from DanubeTech who started the original tutorial for
IIW37 [here](https://github.com/peacekeeper/did-webs-iiw-tutorial)