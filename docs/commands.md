## did:webs Commands

* `dws did keri resolve`
* `dws did keri resolver-service`
* `dws did webs generate`
* `dws did webs service`
* `dws did webs resolve`
* `dws did webs resolver-service`

### did:keri

#### `dws did keri resolve`

**Resolve a did:keri DID.**

Note: This requires a did:keri resolver service to be running as well as the backing witness pool or mailbox used to resolve the OOBI against.

For example, for the did:keri resolver service you would run something like:
```bash
dws did keri resolver-service \
  --name "dws-controller" \
  --config-dir="./local/config/controller" \
  --config-file "dws-controller" \
  --loglevel INFO
```

and have the backing witness pool running with `kli witness demo`. Then you can resolve the did:keri DID with the `dws did keri resolve` command.

```bash
dws did keri resolve \
  --name "dws-controller" \
  --did "did:keri:EBFn5ge82EQwxp9eeje-UMEXF-v-3dlfbdVMX_PNjSft" \
  --oobi "http://127.0.0.1:5642/oobi/EBFn5ge82EQwxp9eeje-UMEXF-v-3dlfbdVMX_PNjSft/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha" \
  --verbose
```

```text
        did:keri:123, oobi    ---------------------------------            ---------------------
   O    ----------------->   |                                 |          |                     |
  -|-   <-----------------   |  dws did keri resolve           |  <---->  |  KERI WATCHER POOL  |
  / \    diddoc, metadata    |                                 |          |                     |
                              ---------------------------------            ---------------------
```

### `dws did keri resolver-service`

**Expose did:keri resolver as an HTTP web service.** (Can be deployed as Universal Resolver driver)

Example:
```bash
dws did keri resolver-service \
  --name "dws-controller" \
  --config-dir="./local/config/controller" \
  --config-file "dws-controller" \
  --port 7678 \
  --loglevel INFO
```

```text
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dws did keri resolver-service  |  <---->  |  KERI WATCHER POOL  |
                             |                                 |          |                     |
                              ---------------------------------            ---------------------
                                            HTTPS
                              HTTP GET      ^   |  200 OK
                              did:keri:123  |   |  diddoc
                              oobi          |   v  metadata

                                              o
                                             -|-
                                             / \
```

## did:webs

### `dws did webs generate`

**Generate DID artifacts for a did:webs DID meaning the did.json DID document and keri.cesr KEL/TEL and ACDC file.**

Example:
```bash
dws did webs generate \
  --name "dws-controller" \
  --output-dir "./local/web/dws" \
  --did "did:webs:127.0.0.1%3A7677:dws:EBFn5ge82EQwxp9eeje-UMEXF-v-3dlfbdVMX_PNjSft"
```

```text
                              ---------------------------------
      did.json, keri.cesr    |                                 |
    --------------------->   |  ANY WEB SERVER  /123/did.json  |
   |                         |                  /123/keri.cesr |
   |    UPLOAD                ---------------------------------
   |
   |      
         did:webs:dom:123     ---------------------------------            ---------------------
   O    ----------------->   |                                 |          |                     |
  -|-   <-----------------   |  dws did webs generate          |  <---->  |  KERI WATCHER POOL  |
  / \   did.json, keri.cesr  |                                 |          |                     |
                              ---------------------------------            ---------------------
```

### `dws did webs service`

The did:webs service acts as a local web server that dynamically generates and serves did.json and keri.cesr files upon request.
you must configure it with a path parameter corresponding to the path embedded within the did:webs DID, otherwise resolution will fail.

The `--meta` argument may optionally be specified to return DID resolution metadata with the did.json DID document.

**Launch web server capable of serving KERI AIDs as did:webs and did:web DIDs.**

The following command configures the did:webs path component to be "dws":

Example:
```text
dws did webs service \
    --name dws-controller \
    --alias labs-id \
    --did-path=dws \
    -p 7677 \
    --config-dir=./local/config/controller \
    --config-file dws-controller \
    --loglevel INFO
```

```text
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dws did webs service           |  <---->  |  KERI WATCHER POOL  |
                             |                                 |          |                     |
                              ---------------------------------            ---------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             {path}/{aid}/did.json  |   |  did.json
                             {path}/{aid}/keri.cesr |   v  keri.cesr

         did:webs:dws:123     ---------------------------------
   O    ----------------->   |                                 |
  -|-   <-----------------   |  ANY DID:WEBS RESOLVER          |  <-----  (verify did.json/keri.cesr)
  / \    diddoc, metadata    |                                 |
                              ---------------------------------
```

```text
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dws did webs service           |  <---->  |  KERI WATCHER POOL  |
                             |                                 |          |                     |
                              ---------------------------------            ---------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                                            |   v          

         did:web:dom:123      ---------------------------------
   O    ----------------->   |                                 |
  -|-   <-----------------   |  ANY DID:WEB RESOLVER           |
  / \         diddoc         |                                 |
                              ---------------------------------
```

### `dws did webs resolve`

Resolving a did:webs DID requires the did:webs resolver service to be running using the `dws did webs resolver-service` command shown below.

The generated DID artifacts are hosted at the directory specified by the `--static-files-dir` argument.

```bash
dws did webs resolver-service \
  --name "dws-controller" \
  --config-dir="./local/config/controller" \
  --config-file "dws-controller" \
  --static-files-dir "./local/web" \
  --loglevel INFO
```

**Resolve a did:webs DID**

Then you may resolve a did:webs DID.

Example:
```bash
dws did webs resolve \
  --name dws-controller \
  --did "did:webs:127.0.0.1%3A7677:dws:EBFn5ge82EQwxp9eeje-UMEXF-v-3dlfbdVMX_PNjSft
```

```text
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dws did webs service           |  <---->  |  KERI WATCHER POOL  |
                             |                                 |          |                     |
                              ---------------------------------            ---------------------
                                                HTTPS
                             HTTP GET           ^   |  200 OK
                             /dws/123/did.json  |   |  did.json
                             /dws/123/keri.cesr |   v  keri.cesr

         did:webs:dws:123     ---------------------------------
   O    ----------------->   |                                 |
  -|-   <-----------------   |  dws did webs resolve           |  <-----  (verify did.json/keri.cesr)
  / \    diddoc, metadata    |                                 |
                              ---------------------------------
```

```text
                              -------------------------------------
                             |                                     |
                             |  ANY WEB SERVER  /dws/123/did.json  |
                             |                  /dws/123/keri.cesr |
                              -------------------------------------
                                                HTTPS
                             HTTP GET           ^   |  200 OK
                             /dws/123/did.json  |   |  did.json
                             /dws/123/keri.cesr |   v  keri.cesr

         did:webs:dws:123     ---------------------------------
   O    ----------------->   |                                 |
  -|-   <-----------------   |  dws did webs resolve           |  <-----  (verify did.json/keri.cesr)
  / \    diddoc, metadata    |                                 |
                              ---------------------------------
```

```text
                              -------------------------------------
                             |                                     |
                             |  ANY WEB SERVER  /dws/123/did.json  |
                             |                  /dws/123/keri.cesr |
                              -------------------------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /dws/123/did.json  |   |  did.json
                                            |   v

         did:web:dom:123     ---------------------------------
   O    ----------------->   |                                 |
  -|-   <-----------------   |  ANY DID:WEB RESOLVER           |
  / \         diddoc         |                                 |
                              ---------------------------------
```

### `dws did webs resolver-service`

**Expose did:webs resolver as an HTTP web service.** (Can be deployed as Universal Resolver driver)

Example:
```bash
dws did webs resolver-service \
  --name "dws-controller" \
  --config-dir="./local/config/controller" \
  --config-file "dws-controller" \
  --static-files-dir "./local/web" \
  --loglevel INFO
```

```text
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dws did webs service           |  <---->  |  KERI WATCHER POOL  |
                             |                                 |          |                     |
                              ---------------------------------            ---------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                             /123/keri.cesr |   v  keri.cesr

                              ---------------------------------
                             |                                 |
                             |  dws did webs resolver-service  |  <-----  (verify did.json/keri.cesr)
                             |                                 |
                              ---------------------------------
                                            HTTPS
                              HTTP GET      ^   |  200 OK
                              did:webs:123  |   |  diddoc
                              oobi          |   v  metadata

                                              o
                                             -|-
                                             / \
```

```text
                              ---------------------------------
                             |                                 |
                             |  ANY WEB SERVER  /123/did.json  |
                             |                  /123/keri.cesr |
                              ---------------------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                             /123/keri.cesr |   v  keri.cesr

                              ---------------------------------
                             |                                 |
                             |  dws did webs resolver-service  |  <-----  (verify did.json/keri.cesr)
                             |                                 |
                              ---------------------------------
                                            HTTPS
                              HTTP GET      ^   |  200 OK
                              did:webs:123  |   |  diddoc
                                            |   v  metadata

                                              o
                                             -|-
                                             / \
```
