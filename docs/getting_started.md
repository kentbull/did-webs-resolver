# did:webs Getting Started guide - for Developers

There are two ways to run the `did:webs` reference implementation:

1. Using the command line with local Python environments. See `./local/did_webs_workflow.sh`.
2. Using Docker to run the `did:webs` reference implementation in a containerized environment. See `./docker/controller-init.sh` and the `docker-compose.yml` file.
    - Run `docker compose up` from one terminal, 
    - then `docker exec -it dws-shell /bin/bash` in a second terminal, and finally,
      - run `dkr did webs resolve --name my-keystore --did did:webs:dws-resolver%3A7677:dws:EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh` to see 
      - `Verification success for did:webs:dws-resolver%3A7677:dws:EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh`
    - See the detailed flow below for more information.

## Credits

Thank you to Markus Sabadello @peacekeeper from DanubeTech who created the original guide for IIW37 [here](https://github.com/peacekeeper/did-webs-iiw-tutorial)

If you're running into trouble in the process below, be sure to check the section [Trouble Shooting](#trouble-shooting) below. 


# Local Command Line Flow (best for development and debugging)

WARNING: This is a work in progress. For now refer to the [Docker Flow](#docker-flow) below.

## Run locally using the command line

Start your witness pool.

Then run the resolver service
```bash
dkr did webs resolver-service \
  --name dws-resolver \
  --config-dir=./local/config/controller \
  --config-file=dws-resolver \
  --static-files-dir ./local/web
```

# Fast Docker Flow (for getting the idea quickly)

This flow is similar to the local command line flow except that the `controller-init.sh` file does not run either the did:webs resolver and does not perform DID resolution with the `dkr did webs resolve` command.
Instead, it only performs did:webs asset generation after which you will perform DID resolution using the `dkr did webs resolve` command in the `dws-shell` container.

You may read the `./docker/controller-init.sh` file to see the commands that it runs and familiarize yourself with the process.

### Prerequisites

If you haven't installed docker on your system yet, first [get it](https://docs.docker.com/get-docker/)

## Run Docker build

Go the root directory of did-webs-resolver repo (this repo) on your local machine. 

Then build all the images with 

```bash
docker compose build --no-cache
```

## Run Docker containers

Next, use the below commands to run the KERI witness network, the `did:webs` artifact generator, the did:webs DID resolver, and the `dws-shell` components.

Make sure to include the `-v` option to remove the volumes so that you can start with a clean slate.

```bash
docker compose down -v
docker compose up -d
```

You may use the `docker logs -f` command to watch the asset generation and resolver logs as they run.

```bash
docker compose logs -f
```

Then perform did:webs DID resolution with:
```bash
dkr did webs resolve \
  --name my-keystore \
  --did did:webs:dws-resolver%3A7677:dws:EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh
```

You will see the following successful output:
```text
Verification success for did:webs:dws-resolver%3A7677:dws:EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh
```

You can see the resolved DID document JSON by including the `--verbose` option to the `dkr did webs resolve` command.
```bash
dkr did webs resolve \
  --name my-keystore \
  --did did:webs:dws-resolver%3A7677:dws:EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh \
  --verbose
```
Viewing the verbose output is left as an exercise for the reader.

# Longer Docker flow (best for learning)

If you want to run each individual command yourself involved in creating an identifier and did:webs DID asset generation then you may use the `dws-shell` command with the steps described below.

## Enter the dws-shell container to peform did:webs DID resolution

```bash
docker compose exec -it dws-shell /bin/bash
cd /dws/scripts
```

## Create your KERI identifier

Alternate paths:

1. You can manually execute the following commands to create your KERI identifier that secures your did:webs DID.
2. OR you can run the script `./get_started.sh` will run the commands for you.

The below steps show the first path, manually executing the commands.

### Step 1: Create a cryptographic salt to secure your KERI identifier

```bash
kli salt
```
The example salt we use in the scripts:
```text
0AAQmsjh-C7kAJZQEzdrzwB7
```


### Step 2: Create the KERI AID `EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh`

#### Initialize KERI environment with name, salt, and config file

**command**:
```bash
kli init --name dws-resolver \
  --salt 0AAQmsjh-C7kAJZQEzdrzwB7 \
  --nopasscode \
  --config-dir /dws/config/controller \
  --config-file get-started
```

**output**:
```bash
KERI Keystore created at: /usr/local/var/keri/ks/get-started
...
Loading 6 OOBIs...
...
Waiting for witness receipts...
```

#### create your AID by creating it's first event, the inception event

**command**:

```bash
kli incept \
  --name get-started \
  --alias my-aid \
  --file /dws/config/controller/incept-with-wan-wit.json
```

**output**:
```text
Prefix  EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG
	Public key 1:  DMJqIvb-YCWj7Ad2Hjq8wm0CgZcXTBcQ1Z-PaJtbv6ji
```

Your AID is `EEMVke69ZjQAXoK3FTLtCwpyWOXx5qkhzIDqXAgYfPgh` and your current public key is `DMJqIvb-YCWj7Ad2Hjq8wm0CgZcXTBcQ1Z-PaJtbv6ji`

#### Additional info

The AID config-file in the container is at ./docker/config/controller/incept-with-wan-wit.json and contains the KERI OOBIs of the witnesses that we'll use:
In this case they are available from the witness network that we started with the docker-compose command above. 

If you `cat` the config at `/dws/config/controller/keri/cf/get-started.json` you should see:

**command**:
```bash
cat /dws/config/controller/keri/cf/get-started.json
```

**config**:
```json
{
    "dt": "2022-01-20T12:57:59.823350+00:00",
    "iurls": [
        "http://witnesses:5642/oobi/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha/controller?name=wan&tag=witness&tag=sample",
        "http://witnesses:5643/oobi/BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM/controller?name=wil&tag=witness&tag=sample",
        "http://witnesses:5644/oobi/BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX/controller?name=wes&tag=witness&tag=sample",
        "http://witnesses:5645/oobi/BM35JN8XeJSEfpxopjn5jr7tAHCE5749f0OobhMLCorE/controller?name=wit&tag=witness&tag=sample",
        "http://witnesses:5646/oobi/BIj15u5V11bkbtAxMA7gcNJZcax-7TgaBMLsQnMHpYHP/controller?name=wub&tag=witness&tag=sample",
        "http://witnesses:5647/oobi/BF2rZTW79z4IXocYRQnjjsOuvFUQv-ptCf8Yltd7PfsM/controller?name=wyz&tag=witness&tag=sample"
    ],
    "keri.cesr.dir": "/dws/web/dws",
    "did.doc.dir": "/dws/web/dws"
}
```

## (Optional) Perform more KERI operations

Optionally use `kli` to perform additional KERI operations such as key rotation, threshold signatures, etc., see KERI docs for details.

See [a key rotation example](#example-key-rotation) below.


## Decide your web address for did:webs

Find a web address (host, optional port, optional path) that you control.

Example web address with host `labs.gleif.org`, no optional port, and optional path `dws:

**web example url**:
```text
https://labs.gleif.org/dws/
```

An example URL for the local Docker setup is as follows:

**docker example url**:
```text
http://dws-resolver%3a7677
```

## Generate your did:webs identifier files using your KERI AID

Note: Replace with your actual web address and AID

You should pick the web address (host, optional port, optional path) where you will host the did:webs identifier. 

For this example we'll use the docker service we've created at host `dws-resolver` and with optional port `7677`. 

**NOTE** the spec requires the colon `:` before an optional port to be encoded as `%3a` in the did:webs identifier.

You can specify the output directory with the `--output-dir` option, which is `/dws/web/dws` in this example.

**command**:
```bash
dkr did webs generate \
  --name get-started \
  --output-dir /dws/web/dws \
  --verbose \
  --did "did:webs:dws-resolver%3a7677:dws:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG"
```

**output**:
```text
keri.cesr:
{"v":"KERI10JSON000159_","t":"icp"...

did.json:
{
  "id": "did:web:dws-resolver%3a7677:dws:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
  "verificationMethod": [
    {...}
  ],
  "service": [
    {...}
  ],
  "alsoKnownAs": []
}
```

This creates files `did.json` and `keri.cesr` under local path:
  - `./docker/artifacts/<your AID>/`, which is mounted to
  - `/dws/web/dws/<your AID>/` in the Docker container.

**command**:
```bash
# from within the dws-shell container
cat /dws/web/dws/EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG/did.json
```

**output**:
This shows the whole JSON document, abbreviated below.
```json
{
  "id": "did:web:dws-resolver%3a7677:dws:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
  "verificationMethod": [...],
  "service": [...],
  "alsoKnownAs": []
}
```

## Host did:webs DID artifacts did.json and keri.cesr

You may use the resolver service to host the DID artifacts with the `--static-files-dir` option or alternatively host them on another web server at an address (host, optional port, optional path) corresponding to the DID created.

You could use git, Github pages, FTP, SCP, etc., or any webserver to host the files as long as you ensure the path component remains the same.

## Example: serve from docker

- Host: `dws-resolver:7677`
- Path: `dws/EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG`

Serving these files is easy and can be done with any web server as long as you ensure the path component remains the same. By path component this means everything **after** the host and port.

For example, for the following did:webs identifier the `dws-resolver%3a7677` comprises the host (`dws-resolver`), URL-encoded port separator (`%3a`), and port (`7677`), and the path component is `dws:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG`.
- `did:web:dws-resolver%3a7677:dws:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG`

Path components, separated by a colon ':' are:
-  `dws` - just a path component, useful for namespacing.
-  `EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG` - the KERI AID of the identifier that generated the did:webs artifacts. 

What this means is that whatever file serving service you use must host the `did.json` and `keri.cesr` at the path:
- `{host}{encoded_port_separator}{port}/{path}/{aid}/`
  - `did.json`
  - `keri.cesr`

The `dws-resolver` service will do this for you if you specify the `--static-files-dir` option to the `dkr did webs resolver-service` command.

You can run the Docker example service to serve the `did.json` and `keri.cesr` files for the other Docker containers:

The commands above, and the `get_started.sh` script, uses the `--output-dir` argument to the `dkr did webs generate` command to specify the directory where the did:webs artifacts are generated.
If you used a different directory then you will need to copy the two files `did.json` and `keri.cesr` to the directory specified in the `--static-files-dir` option of the `dkr did webs resolver-service` command or to whatever webserver you use to host those files.

Let's go into our dws-shell Docker container and see the files:
```bash
docker compose exec -it dws-shell /bin/bash
```

It will serve it at a URL that you can CURL from any of our docker containers (for instance from the webs container) like:

**command**:
```bash
curl -GET http://dws-resolver:7677/dws/EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG/did.json
```
OR from your browser navigate to:
```text
http://127.0.0.1:7677/dws/EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG/did.json
```

**output**:
```json
{
  "id": "did:web:dws-resolver%3a7677:dws:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
  "verificationMethod": [
    {...}
  ],
  "service": [
    {...}
  ],
  "alsoKnownAs": []
}
```

**command**:
```bash
curl -GET http://dws-resolver:7677/EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG/keri.cesr
```
OR from your browser navigate to:
```text
http://127.0.0.1:7677/EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG/keri.cesr
```

**KERI CESR output**:
For readability whitespace is added to the CESR straem below, though it comes with no whitespaces.
```json
// inception event
{
  "v":"KERI10JSON000159_",
  "t":"icp",
  "d":"EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
  "i":"EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
  "s":"0",
  "kt":"1","k":["DMJqIvb-YCWj7Ad2Hjq8wm0CgZcXTBcQ1Z-PaJtbv6ji"],
  "nt":"1","n":["EHUtdHSj8FhR9amkKwz1PQBzgdsQe52NKqynxdXVZuyQ"],
  "bt":"1","b":["BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"],
  "c":[],"a":[]
}
// CESR attachments
-VA--AABAAAk_mN__NcXm2pynD2wxpPPUXVi8brekF_-F1XzTriX-PCMJNYUmzPeQ_2B24sUQjHuMB9oy_EuIrKDeCCucr0N-BABAADE2nej_6ttKC2zEDCasjkDDV5Tc7S-GUGd8NjDbPMNMvyA0w8DgdkfhpTJCQQddtSio8yqFkOjAjGTuJ9PIjkJ-EAB0AAAAAAAAAAAAAAAAAAAAAAA1AAG2025-07-18T20c50c42d897255p00c00
```

### Example: Resolve AID as did:webs using local or remote resolver

In the dws-shell docker container, you can resolve the DID from the dws-resolver:

Resolve the did:webs for the DID:
```bash
dkr did webs resolve --name get-started --did "did:webs:dws-resolver%3a7677:dws:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG"
```


### Add designated aliases attestation ACDC

Because your AID can be served as a did:webs, did:web, did:keri, etc. identifier you can specify these are designated aliases for verification and discovery purposes.
To create this designated aliases attestation, you can execute the following (on the controller docker image or locally with access to the controller's keystore):

**create credential registry command**:
```bash
kli vc registry incept \
  --name get-started \
  --alias my-aid \
  --registry-name dAliases
```

**output**:
```text
Creating designated aliases registry (dAliases) in the get-started keystore...
Waiting for TEL event witness receipts
Sending TEL events to witnesses
Registry:  dAliases(ELLD_gEB_ry65fiAT6J3ShKKhtNnyBUOg-enHfSNezat)
	created for Identifier Prefix:  EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG
```

#### Resolve designated aliases attestation schema

All ACDC credentials/attestations require a schema. Let's resolve the schema for the designated aliases attestation:

**command**:
```bash
kli oobi resolve \
  --name get-started \
  --oobi-alias myDesigAliases \
  --oobi "https://weboftrust.github.io/oobi/EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5"
``` 

**output**:
```text
https://weboftrust.github.io/oobi/EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5 resolved
```

See the attestation attributes and rules under the `./docker/scripts/example-acdc-and-data` and `./docker/scripts/schema/rules` directories.
#### Issuing the designated aliases attestation ACDC 

You can issue the attestation ACDC using the following command, supplying the registry name, schema, attestation attributes and rules:

**command**:
```bash
kli vc create \
  --name get-started \
  --alias my-aid \
  --registry-name dAliases \
  --schema EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5 \
  --data @/dws/scripts/example-acdc-and-data/desig-aliases-attr-public.json \
  --rules @/dws/scripts/schema/rules/desig-aliases-public-schema-rules.json
```

**output**:
```text
Creating designated aliases credential in the dAliases registry...
Waiting for TEL event witness receipts
Sending TEL events to witnesses
EPxvM9FEbFq-wyKtWzNZfUig7v6lH4M6n3ebKRoyldlt has been created.
```
#### List ACDCs to see the designated aliases attestation

To see the attestation you can list the credentials for the registry:

**command**:
```bash
kli vc list \
  --name get-started \
  --alias my-aid \
  --issued \
  --schema EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5
```

**output**:
```text
Current issued credentials for my-aid (EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG):

Credential #1: EPxvM9FEbFq-wyKtWzNZfUig7v6lH4M6n3ebKRoyldlt
    Type: Designated Aliases Public Attestation
    Status: Issued ✔
    Issued by EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG
    Issued on 2023-11-13T17:41:37.710691+00:00
```
#### See the designated aliases attestation ACDC

To see the raw ACDC attestation, you can use the following command:

`command (Note replace <YOUR_REGISTRY>, for example with EOl140-N7hN8qp-LViRfXYNV5RhUO-0n_RPsbMkqm3SJ):`
```bash
kli vc export \
  --name get-started \
  --alias my-aid \
  --said EPxvM9FEbFq-wyKtWzNZfUig7v6lH4M6n3ebKRoyldlt \
  --chain
```

**output**:
Shows the CESR stream (formatted with whitespace for readability), including both the ACDC JSON object at the front of the stream and the CESR attachments at the end of the stream:
```cesr
{
   "v":"ACDC10JSON0005f2_",
   "d":"EPxvM9FEbFq-wyKtWzNZfUig7v6lH4M6n3ebKRoyldlt",
   "i":"EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
   "ri":"ELLD_gEB_ry65fiAT6J3ShKKhtNnyBUOg-enHfSNezat",
   "s":"EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5",
   "a":{
      "d":"EI-8h4KW4Dauwe7liAvBExrA3vUZRWjIvHyD8Xn1UHE_",
      "dt":"2023-11-13T17:41:37.710691+00:00",
      "ids":[
         "did:web:did-webs-service%3a7676:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
         "did:webs:did-webs-service%3a7676:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
         "did:web:example.com:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
         "did:web:foo.com:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
         "did:webs:foo.com:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG"
      ]
   },
   "r":{
      "d":"EEVTx0jLLZDQq8a5bXrXgVP0JDP7j8iDym9Avfo8luLw",
      "aliasDesignation":{
         "l":"The issuer of this ACDC designates the identifiers in the ids field as the only allowed namespaced aliases of the issuer's AID."
      },
      "usageDisclaimer":{
         "l":"This attestation only asserts designated aliases of the controller of the AID, that the AID controlled namespaced alias has been designated by the controller. It does not assert that the controller of this AID has control over the infrastructure or anything else related to the namespace other than the included AID."
      },
      "issuanceDisclaimer":{
         "l":"All information in a valid and non-revoked alias designation assertion is accurate as of the date specified."
      },
      "termsOfUse":{
         "l":"Designated aliases of the AID must only be used in a manner consistent with the expressed intent of the AID controller."
      }
   }
}
-IABEPxvM9FEbFq-wyKtWzNZfUig7v6lH4M6n3ebKRoyldlt0AAAAAAAAAAAAAAAAAAAAAAAEHMHbxs6-9ln3zntcM4JOulKCHDdqAtdEOtw0qloErOZ
```

#### Show designated aliases in generated did:webs artifacts

Now if we re-generate our did:webs identifier the did.json and keri.cesr files will include the attestation information:

**command**:
```bash
# from within the dws-shell container
dkr did webs generate \
  --name get-started \
  --output-dir /dws/web/dws \
  --did "did:webs:dws-resolver%3a7677:dws:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG"
```

And then cURL the keri.cesr to see the new events in the CESR stream:

```bash
curl -GET http://dws-resolver:7677/dws/EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG/keri.cesr
```

**output**:

The KERI CESR output has our original `icp` inception event with our AID and current/next key:

```jsonc
{
  "v": "KERI10JSON000159_",
  "t": "icp",
  "d": "EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
  "i": "EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
  "s": "0",
  "kt": "1",
  "k": [
    "DMJqIvb-YCWj7Ad2Hjq8wm0CgZcXTBcQ1Z-PaJtbv6ji"
  ],
  "nt": "1",
  "n": [
    "EHUtdHSj8FhR9amkKwz1PQBzgdsQe52NKqynxdXVZuyQ"
  ],
  "bt": "1",
  "b": [
    "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
  ],
  "c": [],
  "a": []
}
// CESR attachments
-VA--AABAAAk_mN__NcXm2pynD2wxpPPUXVi8brekF_-F1XzTriX-PCMJNYUmzPeQ_2B24sUQjHuMB9oy_EuIrKDeCCucr0N-BABAADE2nej_6ttKC2zEDCasjkDDV5Tc7S-GUGd8NjDbPMNMvyA0w8DgdkfhpTJCQQddtSio8yqFkOjAjGTuJ9PIjkJ-EAB0AAAAAAAAAAAAAAAAAAAAAAA1AAG2025-07-18T20c50c42d897255p00c00
```

And the new interaction `ixn` event for the registry:
```jsonc
{
  "v": "KERI10JSON00013a_",
  "t": "ixn",
  "d": "EPrcZNm-qeuxdjogRGLJJcGEBTUuy-jfJPTAzZhxdKHf",
  "i": "EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
  "s": "1",
  "p": "EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
  "a": [
    {
      "i": "ELLD_gEB_ry65fiAT6J3ShKKhtNnyBUOg-enHfSNezat",
      "s": "0",
      "d": "ELLD_gEB_ry65fiAT6J3ShKKhtNnyBUOg-enHfSNezat"
    }
  ]
}
// CESR attachments
-VA--AABAACbVNXfoXWo5u0AJWye5njlmQ1qiNYAJVDTMe1io6f8JoWTCaHwiCUDf76K4VdAOEMJ1cYpa1k1gqDMU3k3JaoO-BABAAD-RZrR4a5tcwfdpNTDf-IDfkRZvc0v02pt9OTwgW6AKqQK6biJc-0iEYoUxpBbTPLwIgeoDisNEynZupZR74AC-EAB0AAAAAAAAAAAAAAAAAAAAAAB1AAG2025-07-19T18c37c32d166838p00c00
```

And the new interaction `ixn` event for the attestation:
```jsonc
{
  "v": "KERI10JSON00013a_",
  "t": "ixn",
  "d": "EIK6DjeFUfvFc9jSlzayTS9S6RKb6EIArZQWD3PKc_pK",
  "i": "EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
  "s": "2",
  "p": "EPrcZNm-qeuxdjogRGLJJcGEBTUuy-jfJPTAzZhxdKHf",
  "a": [
    {
      "i": "EPxvM9FEbFq-wyKtWzNZfUig7v6lH4M6n3ebKRoyldlt",
      "s": "0",
      "d": "EHMHbxs6-9ln3zntcM4JOulKCHDdqAtdEOtw0qloErOZ"
    }
  ]
}
// CESR attachments
-VA--AABAAAgZzY8qQjiHFlQGQpfbLJQSKrgsQT6IYqEWJIdjnscWs7IOrzndkCxSIO47hBLfdXS_byx_5lk5zRZ6HPyZEkC-BABAABN9KmfxtCjU1j3LvTDw1LiA9yFfkoa-w18ZYrJUWoPZdoYsgvd18hPms9kv3uPtSb3_nnztC30NkcgOL_JvaMN-EAB0AAAAAAAAAAAAAAAAAAAAAAC1AAG2025-07-19T18c37c34d528630p00c00
```

Inception statement for the Registry
```jsonc
{
  "v": "KERI10JSON0000ff_",
  "t": "vcp",
  "d": "ELLD_gEB_ry65fiAT6J3ShKKhtNnyBUOg-enHfSNezat",
  "i": "ELLD_gEB_ry65fiAT6J3ShKKhtNnyBUOg-enHfSNezat",
  "ii": "EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
  "s": "0",
  "c": [
    "NB"
  ],
  "bt": "0",
  "b": [],
  "n": "0AButF7GiDCmo83JKQKsYBFN"
}
-VAS-GAB0AAAAAAAAAAAAAAAAAAAAAABEPrcZNm-qeuxdjogRGLJJcGEBTUuy-jfJPTAzZhxdKHf
```

Simple Credential (Attestation) Issuance Event `iss`:
```jsonc
{
  "v": "KERI10JSON0000ed_",
  "t": "iss",
  "d": "EHMHbxs6-9ln3zntcM4JOulKCHDdqAtdEOtw0qloErOZ",
  "i": "EPxvM9FEbFq-wyKtWzNZfUig7v6lH4M6n3ebKRoyldlt",
  "s": "0",
  "ri": "ELLD_gEB_ry65fiAT6J3ShKKhtNnyBUOg-enHfSNezat",
  "dt": "2023-11-13T17:41:37.710691+00:00"
}
// CESR attachments
-VAS-GAB0AAAAAAAAAAAAAAAAAAAAAACEIK6DjeFUfvFc9jSlzayTS9S6RKb6EIArZQWD3PKc_pK
```

The ACDC attestation anchored to the TEL:
```jsonc
{
  "v": "ACDC10JSON0005f2_",
  "d": "EPxvM9FEbFq-wyKtWzNZfUig7v6lH4M6n3ebKRoyldlt",
  "i": "EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
  "ri": "ELLD_gEB_ry65fiAT6J3ShKKhtNnyBUOg-enHfSNezat",
  "s": "EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5",
  "a": {
    "d": "EI-8h4KW4Dauwe7liAvBExrA3vUZRWjIvHyD8Xn1UHE_",
    "dt": "2023-11-13T17:41:37.710691+00:00",
    "ids": [
      "did:web:did-webs-service%3a7676:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
      "did:webs:did-webs-service%3a7676:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
      "did:web:example.com:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
      "did:web:foo.com:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
      "did:webs:foo.com:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG"
    ]
  },
  "r": {
    "d": "EEVTx0jLLZDQq8a5bXrXgVP0JDP7j8iDym9Avfo8luLw",
    "aliasDesignation": {
      "l": "The issuer of this ACDC designates the identifiers in the ids field as the only allowed namespaced aliases of the issuer's AID."
    },
    "usageDisclaimer": {
      "l": "This attestation only asserts designated aliases of the controller of the AID, that the AID controlled namespaced alias has been designated by the controller. It does not assert that the controller of this AID has control over the infrastructure or anything else related to the namespace other than the included AID."
    },
    "issuanceDisclaimer": {
      "l": "All information in a valid and non-revoked alias designation assertion is accurate as of the date specified."
    },
    "termsOfUse": {
      "l": "Designated aliases of the AID must only be used in a manner consistent with the expressed intent of the AID controller."
    }
  }
}
-VA0-FABEDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG0AAAAAAAAAAAAAAAAAAAAAAAEDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG-AABAAA9a9__0dZd_rSi5fYDo4FzIpiDYxrUgeiAA5JNc6a2ZkhE6jtuA0uD7F_uSaMIsvBp0nGv_p4SZMu4GK-SvRAM
```

And the DID document now includes the alsoKnownAs field with the designated aliases:
```json
{
  "id": "did:web:dws-resolver%3a7677:dws:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
  "verificationMethod": [
    {
      "id": "#DMJqIvb-YCWj7Ad2Hjq8wm0CgZcXTBcQ1Z-PaJtbv6ji",
      "type": "JsonWebKey",
      "controller": "did:web:dws-resolver%3a7677:dws:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
      "publicKeyJwk": {
        "kid": "DMJqIvb-YCWj7Ad2Hjq8wm0CgZcXTBcQ1Z-PaJtbv6ji",
        "kty": "OKP",
        "crv": "Ed25519",
        "x": "wmoi9v5gJaPsB3YeOrzCbQKBlxdMFxDVn49om1u_qOI"
      }
    }
  ],
  "service": [
    {
      "id": "#BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha/witness",
      "type": "witness",
      "serviceEndpoint": {
        "http": "http://witnesses:5642/",
        "tcp": "tcp://witnesses:5632/"
      }
    }
  ],
  "alsoKnownAs": [
    "did:web:did-webs-service%3a7676:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
    "did:webs:did-webs-service%3a7676:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
    "did:web:example.com:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
    "did:web:foo.com:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG",
    "did:webs:foo.com:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG"
  ]
}
```

### (Optional) Add arbitrary data, like service endpoints, to your KEL

Although your KEL is meant for key state, credentials, etc. a did:webs resolvers can locate other useful information for DID document data such as service endpoints to be packaged along with your KEL.

### (Optional) Resolve AID as did:keri using local resolver

Optionally resolve the AID locally as did:keri, given an OOBI as resolution option.

Note: Replace with your actual AID

```bash
dkr did keri resolve \
    --name get-started \
    --did did:keri:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG \
    --oobi http://witnesses:5642/oobi/EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
```

### Resolve as did:web using Universal Resolver

https://dev.uniresolver.io/#did:web:peacekeeper.github.io:did-webs-iiw37-tutorial:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP

### Resolve as did:webs using Universal Resolver

https://dev.uniresolver.io/#did:webs:peacekeeper.github.io:did-webs-iiw37-tutorial:EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP

### Example key rotation

Use the following two commands in your running Docker container.

```bash
kli rotate --name get-started --alias my-aid
```
Be sure to repeat the `dkr webs generate` command:

```bash
dkr did webs generate --name get-started --did did:webs:dws-resolver%3a7677:dws:EDOIYUazXNmI0A9Xahe3nw1-8iwpZcMLz-6sdrSyPucG
```
Now upload the overwritten `did.json` and `keri.cesr` again to the hosted public location.
