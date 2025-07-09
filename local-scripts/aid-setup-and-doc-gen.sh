#!/bin/bash
# aid-setup-and-doc-gen.sh
# Sets up the local AID for use by did:webs with one witness and then
# generates the DID document and KERI CESR stream for that AID.
#
# Note: this script requires it be run from the root did-webs-resolver directory

CWD="${PWD##*/}"
if [ "${CWD}" != "did-webs-resolver" ]; then
    echo "This script must be run from the root did-webs-resolver directory. It was run from the directory: ${CWD}"
    exit 1
fi

source ./local-scripts/color-printing.sh

# Binary Dependencies
command -v kli >/dev/null 2>&1 || { print_red "kli is not installed or not available on the PATH. Aborting."; exit 1; }
command -v dkr >/dev/null 2>&1 || { print_red "dkr is not installed or not available on the PATH. Aborting."; exit 1; }

# need to run witness network
print_dark_gray "Assumes witnesses started and running..."
WAN_PRE=BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
WIT_HOST=http://127.0.0.1:5642
WIT_OOBI="${WIT_HOST}/oobi/${WAN_PRE}"
curl $WIT_OOBI >/dev/null 2>&1
status=$?
if [ $status -ne 0 ]; then
    print_red "Witness server not running at ${WIT_HOST}"
    exit 1
else
    print_dark_gray "Witness server is running at ${WIT_OOBI}\n"
fi

# Set up identifying information for the controller AID and the did:webs DID
DOMAIN=labs.hyperledger.org
print_dark_gray "Creating controller AID and did:webs for ${DOMAIN}"
NAME="hyperledger"
ALIAS="labs-id"
# init environment for controller AID
exists=$(kli aid --name "${NAME}" --alias "${ALIAS}" 2>/dev/null)
if [[ "${exists}" =~ ^E  || ! "${exists}" =~ Keystore* ]] ; then
  print_yellow "already exists, reusing ${exists}"
else
  print_dark_gray "does not exist, creating..."
  kli init \
    --name "${NAME}" \
    --salt 0AAFmiyF5LgNB3AT6ZkdN25B \
    --nopasscode \
    --config-dir "./local-config" \
    --config-file "${NAME}"

  # inception for controller AID
  kli incept \
    --name "${NAME}" \
    --alias "${ALIAS}" \
    --file "./local-config/incept-with-wan-wit.json"
fi

MY_AID=$(kli aid --name "${NAME}" --alias "${ALIAS}")
MY_OOBI="http://127.0.0.1:5642/oobi/${MY_AID}/witness/${WAN_PRE}"

# check witness oobi for our AID
curl "${MY_OOBI}" >/dev/null 2>&1
status=$?
if [ $status -ne 0 ]; then
    print_red "Controller ${NAME}/${ALIAS} with AID ${MY_AID} not found at ${MY_OOBI}"
    exit 1
else
    print_green "Controller ${NAME}/${ALIAS} with AID ${MY_AID} setup complete.\n"
fi

# generate controller did:webs for DOMAIN
print_dark_gray "Generating did:webs for ${NAME} on ${DOMAIN} with AID ${MY_AID} to ./local-web"
dkr did webs generate \
  --name "${NAME}" \
  --output-dir "./local-web" \
  --did did:webs:"${DOMAIN}":did-webs-resolver:pages:"${MY_AID}"
