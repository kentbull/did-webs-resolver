# did:webs development roadmap

This document shows the current status of the did:webs project and future plans.

## Current Features

- **Static DID Asset Generation**: Create did.json and keri.cesr files based on a local AID's state in the local keystore (Habery).
- **Dynamic DID Asset Generation**: Using the HTTP endpoints, dynamically generate did.json and keri.cesr files based on the current local state of an AID.
- Designated Aliases support: Issue self-attested ACDCs with designated aliases (names) with the correct schema and they automatically show up in the `alsoKnownAs` portion of the DID document.
- **did:webs DID Resolution**: Resolve did:webs DIDs based on the available did.json and keri.cesr files.
- **did:keri DID Resolution**: Resolve did:keri DIDs based on the response to an OOBI resolution for an AID.
- **Universal Resolver Support**: The UniversalResolverResource supports the [Universal Resolver](https://dev.uniresolver.io/) by Markus Sabadello.
- **Static DID Asset Hosting**: Serve static did.json and keri.cesr files for local AIDs via HTTP endpoints.

## Future Plans

- **Strict Dynamic DID Asset Hosting for Remote AIDs**: Lock down the HTTP DID asset generation endpoints to return did:webs assets for only an allowed set of AIDs.
- **Import of DID Assets for Remote AIDs**: Allow for importing of CESR streams for remote AIDs so that the local dynamic DID asset generation can be used for remote AIDs.
- **Remove the Static DID Asset Hosting**: As hosting static did.json and keri.cesr files for remote AIDs is not secure, we will remove the static hosting of these files.