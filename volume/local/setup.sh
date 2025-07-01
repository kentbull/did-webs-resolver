#!/bin/bash
# Sets up the local AID with one witness

# need to run witness network
echo "Assumes witnesses started and running..."

DOMAIN=labs.hyperledger.org
echo "Creating controller AID and did:webs for ${DOMAIN}"
NAME="hyperledger"
ALIAS="labs-id"
# init environment for controller AID
exists=$(kli aid --name "${NAME}" --alias "${ALIAS}" 2>/dev/null)
if [[ "${exists}" =~ ^E  || ! "${exists}" =~ Keystore* ]] ; then
  echo "already exists, reusing ${exists}"
else
  echo "does not exist, creating..."
  kli init \
    --name "${NAME}" \
    --salt 0AAFmiyF5LgNB3AT6ZkdN25B \
    --nopasscode \
    --config-dir "./config" \
    --config-file local

  # inception for controller AID
  kli incept \
    --name "${NAME}" \
    --alias "${ALIAS}" \
    --file "./config/incept-with-wan-wit.json"
fi

MY_AID=$(kli aid --name "${NAME}" --alias "${ALIAS}")
WAN_AID="BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"

# check witness oobi for our AID
curl http://127.0.0.1:5642/oobi/"${MY_AID}"/witness/"${WAN_AID}"

# generate controller did:webs for DOMAIN
dkr did webs generate \
  --name "${NAME}" \
  --did did:webs:"${DOMAIN}":did-webs-resolver:pages:"${MY_AID}"
