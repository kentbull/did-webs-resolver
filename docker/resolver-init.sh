#!/usr/bin/env bash
# resolver-init.sh
# Initializes the KERI AID for the dws-resolver controller to be used in the UniversalResolverResource to support
# web requests like:
#   curl http://dws-resolver:7677/1.0/identifiers/did:webs:dws-static-service%3A7679:dws:EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh
# This includes the following:
#   - set up the dws-controller keystore
#   - resolve the designated aliases ACDC schema (allows parsing of designated alias ACDC CESR streams for alsoKnownAs and equivalentIds)
#   - start the resolver service on port 7677

CONFIG_DIR="/dws/config"

kli init \
  --name "dws-resolver" \
  --nopasscode \
  --config-dir "${CONFIG_DIR}/controller" \
  --config-file "dws-resolver"

DESG_ALIASES_SCHEMA="EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5"
kli oobi resolve \
  --name "dws-resolver" \
  --oobi-alias "designated-alias-public" \
  --oobi "https://weboftrust.github.io/oobi/${DESG_ALIASES_SCHEMA}"

dws did webs resolver-service \
    --http 7677 \
    --name dws-resolver \
    --config-dir /dws/config/controller \
    --config-file dws-resolver \
    --loglevel INFO
