#!/bin/bash
# get_started.sh
# Sets up the local AID for use by did:webs with one witness and then
# generates the DID document and KERI CESR stream for that AID.
# Notes:
#   - See the GETTING_STARTED.md for those instructions.
#   - This script does not use passcodes for simplicity. Use `kli passcode generate` and the `--passcode` option when you need one.

RESOLVER_HOST="dws-resolver"
RESOLVER_PORT="7677"
MY_AID="EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG"
MY_DID="did:webs:${RESOLVER_HOST}%3a${RESOLVER_PORT}:dws:${MY_AID}"
MY_SALT="0AAQmsjh-C7kAJZQEzdrzwB7"  # Can create a new one with `kli salt`

kli init \
  --name get-started \
  --salt "${MY_SALT}" \
  --nopasscode \
  --config-dir /dws/config/controller \
  --config-file get-started

kli incept \
  --name get-started \
  --alias my-aid \
  --file /dws/config/controller/incept-with-wan-wit.json

echo ""
read -p "Press enter to generate did:webs..."

dkr did webs generate \
  --name get-started \
  --output-dir /dws/web/dws \
  --did "${MY_DID}"

dkr did webs generate \
  --name get-started \
  --output-dir /dws/web/dws \
  --verbose \
  --did "did:webs:dws-resolver%3a7677:dws:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG"

echo ""
echo "ATTENTION: In your did-webs-service, start the webs server first, see the GETTING_STARTED.md for those instructions"
read -p "Press enter to resolve did:webs..."

dkr did webs resolve \
  --name get-started \
  --did "${MY_DID}"

echo ""
read -p "Press enter to create designated aliases..."

echo
echo "Creating designated aliases registry (dAliases) in the get-started keystore..."
kli vc registry incept \
  --name get-started \
  --alias my-aid \
  --registry-name dAliases

# Pull in designated aliases schema
kli oobi resolve \
  --name get-started \
  --oobi-alias myDesigAliases \
  --oobi "https://weboftrust.github.io/oobi/EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5"

kli saidify --file /dws/scripts/example-acdc-and-data/desig-aliases-attr-public.json

echo
echo "Creating designated aliases credential in the dAliases registry..."
kli vc create \
  --name get-started \
  --alias my-aid \
  --registry-name dAliases \
  --schema EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5 \
  --data @/dws/scripts/example-acdc-and-data/desig-aliases-attr-public.json \
  --rules @/dws/scripts/schema/rules/desig-aliases-public-schema-rules.json

echo
echo "Showing credentials in the dAliases registry for this AID..."
kli vc list \
  --name get-started \
  --alias my-aid \
  --issued \
  --schema EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5

SAID=$(kli vc list \
  --name get-started \
  --alias my-aid \
  --issued \
  --said \
  --schema EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5)

echo
echo
echo "Showing the ACDC data for the designated aliases credential..."
echo
kli vc export \
  --name get-started \
  --alias my-aid \
  --said "$SAID" \
  --chain
echo

echo ""
read -p "Press enter generate did:webs with designated aliases..."

dkr did webs generate \
  --name get-started \
  --output-dir /dws/web/dws \
  --did "${MY_DID}"

echo ""
read -p "Press enter to resolve did:webs with designated aliases..."

dkr did webs resolve \
  --name get-started \
  --did "${MY_DID}" \
  --verbose

echo
echo
echo "did:webs generation and resolution with designated aliases completed."
