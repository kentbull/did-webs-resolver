#!/usr/bin/env bash
# test-resolutions.sh
# Tests resolving did:webs and did:keri DIDs using both the CLI commands and the HTTP requests to the UniversalResolverResource.

source /dws/color-printing.sh

echo
print_yellow "-----------------------------Test Resolutions for did:webs and did:keri-----------------------------"
echo

print_yellow "Setting up the resolving entity's keystore (dws) to have the designated aliases ACDC schema..."
# "dws" is the default keystore name, makes the CLI commands shorter
kli init --name "dws" --nopasscode --config-dir "/dws/config/controller" --config-file "dws"
kli oobi resolve --name "dws" --oobi-alias "designated-alias-public" --oobi "https://weboftrust.github.io/oobi/EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5"
echo
echo

# DIDs
DID_WEBS_DID_STATIC_HOST="did:webs:dws-static-service%3A7679:dws:EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh"
print_yellow "DID_WEBS_DID_STATIC_HOST: ${DID_WEBS_DID_STATIC_HOST}"
DID_WEBS_DID_DYNAMIC_HOST="did:webs:dws-dynamic-service%3A7680:dws:EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh"
print_yellow "DID_WEBS_DID_DYNAMIC_HOST: ${DID_WEBS_DID_DYNAMIC_HOST}"

DID_KERI_AID_CONTROLLER_WITNESS_OOBI="http://witnesses:5642/oobi/EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
DID_KERI_DID="did:keri:EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh"
print_yellow "did:keri base AID: ${DID_KERI_DID}"
DID_KERI_DID_WITH_OOBI="${DID_KERI_DID}?oobi=${DID_KERI_AID_CONTROLLER_WITNESS_OOBI}"
print_yellow "did:keri with witness OOBI: ${DID_KERI_DID_WITH_OOBI}"

# WARNING: There's a bug in the Docker setup where the resolving entity is not processing the reply 'rpy' messages for the
#   witness of the controller AID so as a temporary workaround an OOBI resolution is used to resolve the AID's witness OOBI
#   to bring those reply messages for the location scheme messages into the local keystore (dws).
#   What is supposed to happen is that these loc scheme messages, which are in the keri.cesr stream, are supposed to be
#   processed during the "save_cesr" function during DID resolution. This works with the universal resolver calls but not
#   with the CLI commands. We need to investigate this further. It only occurs in Docker. The local setup works fine.
#   TODO investigate the bug in the Docker setup for the resolving entity's keystore (dws) not processing the reply messages.
#        see issue https://github.com/hyperledger-labs/did-webs-resolver/issues/80

# Tell the resolving entity's keystore (dws) about the controller AID's location scheme messages for its witness via witness OOBI resolution
kli oobi resolve --name "dws" --oobi-alias "controller-witness-oobi" --oobi "${DID_KERI_AID_CONTROLLER_WITNESS_OOBI}"

# Test resolutions against the static service for a did:webs DID
echo
print_lcyan "resolving did:webs DID using the CLI..."
echo

# example did:webs DID:
#     did:webs:dws-static-service%3A7679:dws:EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh
dkr did webs resolve --did "${DID_WEBS_DID_STATIC_HOST}"
status=$?
if [ $status -ne 0 ]; then
    print_red "Failed to resolve did:webs DID"
    exit $status
else
    echo
    print_green "Successfully resolved did:webs DID using the CLI"
fi

# Test resolution using the local keystore with the witness OOBI for a did:keri DID
echo
print_lcyan "resolving did:keri DID using the CLI..."
echo

# example did:keri DID:
#     did:keri:EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh?oobi=http://witnesses:5642/oobi/EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
dkr did keri resolve --did "${DID_KERI_DID_WITH_OOBI}"

status=$?
if [ $status -ne 0 ]; then
    print_red "Failed to resolve did:keri DID"
    exit $status
else
    echo
    print_green "Successfully resolved did:keri DID using the CLI"
fi

RESOLVER_BASE_URL="http://dws-resolver:7677/1.0/identifiers"
echo
print_lcyan "resolving did:webs DID using the HTTP request using the static host..."
echo

# example did:webs DID URL with the UniversalResolverResource using the static host:
#     http://dws-resolver:7677/1.0/identifiers/did:webs:dws-static-service%3A7679:dws:EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh
curl "${RESOLVER_BASE_URL}/${DID_WEBS_DID_STATIC_HOST}"
status=$?
if [ $status -ne 0 ]; then
    echo "Failed to resolve did:webs DID via HTTP request"
    exit $status
else
    echo
    echo "Successfully resolved did:webs DID using the HTTP request"
fi

echo
print_lcyan "resolving did:keri DID using the HTTP request using the static host..."
echo

# example did:keri DID URL with the UniversalResolverResource using OOBI resolution for the did:keri AID's KEL:
#     http://dws-resolver:7677/1.0/identifiers/did:keri:EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh?oobi=http://witnesses:5642/oobi/EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
curl "${RESOLVER_BASE_URL}/${DID_KERI_DID_WITH_OOBI}"
status=$?
if [ $status -ne 0 ]; then
    print_red "Failed to resolve did:keri DID via HTTP request"
    exit $status
else
    echo
    print_green "Successfully resolved did:keri DID using the HTTP request"
fi

echo
print_lcyan "resolving did:webs DID using the HTTP request using the dynamic host..."
echo

# example did:webs DID URL with the UniversalResolverResource using the dynamic host:
#     http://dws-resolver:7677/1.0/identifiers/did:webs:dws-dynamic-service%3A7680:dws:EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh
curl "${RESOLVER_BASE_URL}/"${DID_WEBS_DID_DYNAMIC_HOST}
status=$?
if [ $status -ne 0 ]; then
    print_red "Failed to resolve did:webs DID via HTTP request using the dynamic host"
    exit $status
else
    echo
    print_green "Successfully resolved did:webs DID using the HTTP request using the dynamic host"
fi

echo
print_green "-----------------------------All resolutions succeeded-----------------------------"
echo