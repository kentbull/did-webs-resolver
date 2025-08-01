#!/bin/bash
# did_webs_workflow.sh
# Sets up the local AID for use by did:webs with one witness and then
# generates the DID document and KERI CESR stream for that AID.
#
# Note: this script requires it be run from the root did-webs-resolver directory
#   - `kli witness demo` should be running in another terminal.
CONFIG_DIR="./local/config"
SCRIPTS_DIR="./local"
WEB_DIR="./local/web"
ARTIFACT_PATH="dws"
source "${SCRIPTS_DIR}"/color-printing.sh

# cleanup
static_service_pid=""
resolver_service_pid=""

trap cleanup INT
trap cleanup ERR
trap cleanup EXIT

function cleanup() {
  print_dark_gray "Cleaning up..."
  if [[ -n "${static_service_pid}" ]]; then
    kill "${static_service_pid}" >/dev/null 2>&1
    print_dark_gray "Killed static service with PID ${static_service_pid}"
  fi
  if [[ -n "${resolver_service_pid}" ]]; then
    kill "${resolver_service_pid}" >/dev/null 2>&1
    print_dark_gray "Killed resolver service with PID ${resolver_service_pid}"
  fi
}

function pause() {
    # shellcheck disable=SC2162
    read -p "$*"
}

METADATA_TRUE=$1
print_yellow "METADATA_TRUE: ${METADATA_TRUE}"

CWD="${PWD##*/}"
if [ "${CWD}" != "did-webs-resolver" ]; then
    echo "This script must be run from the root did-webs-resolver directory. It was run from the directory: ${CWD}"
    exit 1
fi

# Binary Dependencies
command -v kli >/dev/null 2>&1 || { print_red "kli is not installed or not available on the PATH. Aborting."; exit 1; }
command -v dkr >/dev/null 2>&1 || { print_red "dkr is not installed or not available on the PATH. Aborting."; exit 1; }

# need to run witness network
DOMAIN=127.0.0.1
DID_PORT=7678
print_dark_gray "Assumes witnesses started and running..."
WAN_PRE=BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha

function check_witnesses() {
  WIT_HOST=http://"${DOMAIN}":5642
  WIT_OOBI="${WIT_HOST}/oobi/${WAN_PRE}"
  curl $WIT_OOBI >/dev/null 2>&1
  status=$?
  if [ $status -ne 0 ]; then
      print_red "Witness server not running at ${WIT_HOST}"
      exit 1
  else
      print_dark_gray "Witness server is running at ${WIT_OOBI}\n"
  fi
}
check_witnesses

# Set up identifying information for the controller AID and the did:webs DID
KEYSTORE_NAME="dws-controller"
AID_ALIAS="labs-id"
DESG_ALIASES_REG="did:webs_designated_aliases"
DESG_ALIASES_SCHEMA="EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5"
print_dark_gray "Creating controller AID ${KEYSTORE_NAME}/${AID_ALIAS} and did:webs for ${DOMAIN}"
# init environment for controller AID

MY_OOBI=""
MY_AID=""
function create_aid() {
  # Create keystore, AID, verify witness accessibility, and resolve the designated aliases schema
  kli init --name "${KEYSTORE_NAME}" --salt 0AAFmiyF5LgNB3AT6ZkdN25B --nopasscode --config-dir "${CONFIG_DIR}/controller" --config-file "${KEYSTORE_NAME}"
  # inception for controller AID
  kli incept --name "${KEYSTORE_NAME}" --alias "${AID_ALIAS}" --file "${CONFIG_DIR}/controller/incept-with-wan-wit.json"

  # check witness oobi for our AID
  MY_AID=$(kli aid --name "${KEYSTORE_NAME}" --alias "${AID_ALIAS}")
  MY_OOBI="http://${DOMAIN}:5642/oobi/${MY_AID}/witness/${WAN_PRE}"
  curl "${MY_OOBI}" >/dev/null 2>&1
  status=$?
  if [ $status -ne 0 ]; then
      print_red "Controller ${KEYSTORE_NAME}/${AID_ALIAS} with AID ${MY_AID} not found at ${MY_OOBI}"
      exit 1
  else
      print_green "Controller ${KEYSTORE_NAME}/${AID_ALIAS} with AID ${MY_AID} setup complete."
  fi
}

function set_up_aid() {
  exists=$(kli aid --name "${KEYSTORE_NAME}" --alias "${AID_ALIAS}" 2>/dev/null)
  if [[ "${exists}" =~ ^E  || ! "${exists}" =~ Keystore* ]] ; then
    print_dark_gray "${KEYSTORE_NAME}/${AID_ALIAS} already exists, reusing ${exists}"
  else
    print_dark_gray "does not exist, creating..."
    create_aid
    kli oobi resolve --name "${KEYSTORE_NAME}" \
      --oobi-alias "designated-alias-public" \
      --oobi "https://weboftrust.github.io/oobi/${DESG_ALIASES_SCHEMA}"
  fi
}
set_up_aid


DESIG_ALIASES_FILE="${SCRIPTS_DIR}/designated_aliases.json"

function create_designated_aliases_json() {
  timestamp=$(kli time | tr -d '[:space:]')
    read -r -d '' DESIG_ALIASES_JSON << EOM
{
  "d": "",
  "dt": "${timestamp}",
  "ids": [
    "did:web:${DOMAIN}%3a${DID_PORT}:${MY_AID}",
    "did:webs:${DOMAIN}%3a${DID_PORT}:${MY_AID}",
    "did:web:example.com:${MY_AID}",
    "did:web:foo.com:${MY_AID}",
    "did:webs:foo.com:${MY_AID}"
  ]
}
EOM
    print_lcyan "building designated aliases JSON: ${DESIG_ALIASES_FILE}"
    echo "$DESIG_ALIASES_JSON" > "${DESIG_ALIASES_FILE}"
    kli saidify --file "${DESIG_ALIASES_FILE}"
    ALIASES=$(< "${DESIG_ALIASES_FILE}" jq)
    print_lcyan "${ALIASES}"
}

function create_desg_aliases_registry() {
  kli vc registry incept \
    --name "${KEYSTORE_NAME}" \
    --alias "${AID_ALIAS}" \
    --registry-name "${DESG_ALIASES_REG}"
  print_green "Created designated aliases registry ${KEYSTORE_NAME}/${AID_ALIAS} with AID ${MY_AID}"
}

function create_desg_aliases_cred() {
  kli vc create \
    --name "${KEYSTORE_NAME}" \
    --alias "${AID_ALIAS}" \
    --registry-name "${DESG_ALIASES_REG}" \
    --schema "${DESG_ALIASES_SCHEMA}" \
    --data @"${DESIG_ALIASES_FILE}" \
    --rules @"${SCRIPTS_DIR}/schema/rules/desig-aliases-public-schema-rules.json"
  print_green "Created designated aliases credential for ${KEYSTORE_NAME}/${AID_ALIAS} with AID ${MY_AID}"
}

function prep_aliases(){
  REGISTRY=$(kli vc registry list --name "${KEYSTORE_NAME}" | awk '{print $1}') # Get the first column which is the registry name
  if [ -n "${REGISTRY}" ]; then
      print_dark_gray "Designated Aliases attestation registry already created"
  else
    create_desg_aliases_registry
  fi
  # Add self-attested DIDs for the controller AID
  SAID=$(kli vc list --name "${KEYSTORE_NAME}" --alias "${AID_ALIAS}" --issued --said \
        --schema "${DESG_ALIASES_SCHEMA}")
    if [ -n "${SAID}" ]; then
        print_dark_gray "Designated aliases credential already created"
    else
      create_designated_aliases_json
      create_desg_aliases_cred
    fi
}
prep_aliases

# View issued designated aliases VC
echo
kli vc list --name "${KEYSTORE_NAME}" --alias "${AID_ALIAS}" --issued \
  --schema "${DESG_ALIASES_SCHEMA}"
echo

# generate controller did:webs for DOMAIN
# example: did:webs:127.0.0.1%3A7678:dws:EBFn5ge82EQwxp9eeje-UMEXF-v-3dlfbdVMX_PNjSft
DID_WEBS_DID="did:webs:${DOMAIN}%3A${DID_PORT}:${ARTIFACT_PATH}:${MY_AID}"
DID_KERI_DID="did:keri:${MY_AID}"
print_yellow "Generating did:webs DID for ${KEYSTORE_NAME} on ${DOMAIN} with AID ${MY_AID} in ${WEB_DIR}/${ARTIFACT_PATH}"
print_yellow "       of: ${DID_WEBS_DID}"

#pause "Press Enter to generate the did:webs DID document and KERI CESR stream..."
if [[ "${METADATA_TRUE}" = true ]] ; then
  print_yellow "Using metadata for artifact generation"
  dkr did webs generate \
    --name "${KEYSTORE_NAME}" \
    --config-dir ./local/config/controller \
    --config-file "${KEYSTORE_NAME}" \
    --output-dir "${WEB_DIR}/${ARTIFACT_PATH}" \
    --did "${DID_WEBS_DID}" \
    --meta # include DID generation metadata as envelope of DID document in did.json
else
  print_yellow "Not using metadata for artifact generation"
  dkr did webs generate \
    --name "${KEYSTORE_NAME}" \
    --config-dir ./local/config/controller \
    --config-file "${KEYSTORE_NAME}" \
    --output-dir "${WEB_DIR}/${ARTIFACT_PATH}" \
    --did "${DID_WEBS_DID}"
fi

# -------------------------------------------------
# Resolution of Static Artifacts from command line
# -------------------------------------------------


# Initialize dws-resolver keystore so it knows about the designated aliases schema and will not put the designated aliases ACDCs in the missing signature escrow.
kli init --name "dws-resolver" --nopasscode --config-dir "${CONFIG_DIR}/controller" --config-file "dws-resolver"
kli oobi resolve --name "dws-resolver" \
    --oobi-alias "designated-alias-public" \
    --oobi "https://weboftrust.github.io/oobi/${DESG_ALIASES_SCHEMA}"

# STATIC FILE MODE: Run the resolver service in static file server mode to serve the generated did:webs assets
dkr did webs resolver-service \
  --http 7678 \
  --name "static-service" \
  --config-dir="${CONFIG_DIR}/controller" \
  --config-file "static-service" \
  --static-files-dir "${WEB_DIR}" \
  --did-path "${ARTIFACT_PATH}" &
print_lcyan "did:webs static service started on http://${DOMAIN}:7678 serving files from ${WEB_DIR}/${ARTIFACT_PATH}"
static_service_pid=$!

sleep 1.5 # Give the static service time to start

# Resolve the did:webs DID using the static service
#pause "Press Enter to resolve the did:webs DID using CLI resolution..."
# Sample DID: "did:webs:127.0.0.1%3A7678:dws:EBFn5ge82EQwxp9eeje-UMEXF-v-3dlfbdVMX_PNjSft
status=0
function resolve_didwebs(){
  if [[ "${METADATA_TRUE}" = true ]] ; then
    print_yellow "Using metadata for did:webs resolution"
    dkr did webs resolve --name "dws-resolver" \
      --did "${DID_WEBS_DID}" \
      --meta # include DID resolution metadata as envelope of DID document in did.json
    status=$?
  else
    print_yellow "Not using metadata for did:webs resolution"
    dkr did webs resolve --name "dws-resolver" \
      --did "${DID_WEBS_DID}"
    status=$?
  fi
  if [ $status -ne 0 ]; then
      print_red "DID resolution failed for ${DID_WEBS_DID}"
      exit 1
  else
      print_green "DID resolution succeeded for ${DID_WEBS_DID}"
  fi
}
resolve_didwebs

#pause "Press Enter to resolve the did:keri DID using an OOBI resolution service..."
status=0
function resolve_didkeri(){
  if [[ "${METADATA_TRUE}" = true ]] ; then
    print_yellow "Using metadata for ${DID_KERI_DID} resolution"
    print_dark_gray "Resolving OOBI: ${MY_OOBI} for ${DID_KERI_DID}"
    dkr did keri resolve \
      --name "dws-resolver" \
      --did "${DID_KERI_DID}" \
      --oobi "${MY_OOBI}" \
      --meta
    status=$?
  else
    print_yellow "Not using metadata for did:keri resolution"
    print_dark_gray "Resolving OOBI: ${MY_OOBI} for ${DID_KERI_DID}"
    dkr did keri resolve \
      --name "dws-resolver" \
      --did "${DID_KERI_DID}" \
      --oobi "${MY_OOBI}"
    status=$?
  fi
  if [ $status -ne 0 ]; then
      print_red "DID resolution failed for ${DID_WEBS_DID}"
      exit 1
  else
      print_green "DID resolution succeeded for ${DID_KERI_DID}"
  fi
}
resolve_didkeri

# -------------------------------------------------
# Resolution using the universal resolver service via /1.0/identifiers/{did} endpoint
# -------------------------------------------------

# UNIVERSAL RESOLVER MODE: Run the resolver service as only a did:webs and did:keri resolver
dkr did webs resolver-service \
  --http 7676 \
  --name "dws-resolver" \
  --config-dir="${CONFIG_DIR}/controller" \
  --config-file "dws-resolver" &
print_lcyan "did:webs universal resolver service started on http://${DOMAIN}:7676"
resolver_service_pid=$!

sleep 1.5 # Give the resolver service time to start

# Resolve did:webs using the universal resolver service
#pause "Press Enter to resolve the did:webs DID using the universal resolver service..."
curl "http://${DOMAIN}:7676/1.0/identifiers/${DID_WEBS_DID}" >/dev/null 2>&1
status=$?
if [ $status -ne 0 ]; then
    print_red "Universal resolver service did:webs resolution failed for ${DID_WEBS_DID}"
    exit 1
else
    print_green "Universal resolver service did:webs resolution succeeded for ${DID_WEBS_DID}"
fi

#pause "Press Enter to resolve the did:keri DID using the universal resolver service..."
curl "http://${DOMAIN}:7676/1.0/identifiers/${DID_KERI_DID}?oobi=${MY_OOBI}" >/dev/null 2>&1
status=$?
if [ $status -ne 0 ]; then
    print_red "Universal resolver service did:keri resolution failed for did:keri:${MY_AID}"
    exit 1
else
    print_green "Universal resolver service did:keri resolution succeeded for did:keri:${MY_AID}"
fi

echo
print_green "DID:webs workflow completed successfully."
echo
