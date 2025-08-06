# did:webs troubleshooting document

Using the did:webs artifact generator and resolver.

### If you are using an Apple Silicon (M1) mac then you might need to:
* In Docker, select `Use Rosetta for x86/amd64 emulation on Apple Silicon`
* Before running docker compose `export DOCKER_DEFAULT_PLATFORM=linux/amd64`

### Your docker container is already up- and running?

#### Do you have a witness up for another identifier?
Then the `kli incept --name get-started --alias my-aid --file "/dws/config/controller/incept-with-wan-wit.json"` command will give this response:

`ERR: Already incepted pre=[Your prefix of another AID].`
 
#### Solution
Various solutions if you're a Docker expert. If not, we'll go down the more rigorous path:

1. Step out of the running container with `exit` 
2. and then `docker compose down -v`. This should respond with:

[+] Running 3/3
 ⠿ Container dkr                            Removed  
 ⠿ Container witnesshost                    Removed   
 ⠿ Network did-webs-iiw37-tutorial_default  Removed 
Now you could continue with:
```
docker compose up -d
docker compose exec -it dws-shell /bin/bash
```
### Special attention Github Pages: web address

There's no problem that we know of when you use Github pages in a bare-bones manner. However, if you use static page generators to populate your github pages (e.g. Jekyll or Docusaurus) be sure to choose the right spot of your files and extract the right paths of the links needed to resolve:

#### Example
This is the web address of the `docusaurus` directory:
https://weboftrust.github.io/WOT-terms/test/did-webs-iiw37-tutorial/

But the exact spot to extract the files as text would be something like:
```
http://raw.githubusercontent.com/WOT-terms/test/did-webs-iiw37-tutorial/[your AID] 
```
The reason for this confusion is that a static page generator like Docusaurus or Jekyll might interfere with the location, visibility and accessibility of your files on Github Pages.

We advise to choose a simple public directory that you control and we won't go into more detail on how to deal with static site generators.

Example:
```
dkr did keri resolve --name dkr --did did:keri:EPaP4GgZsB6Ww-SeSO2gwNDMNpC7-DN51X5AqiJFWkw6 --oobi http://witnesshost:5642/oobi/EPaP4GgZsB6Ww-SeSO2gwNDMNpC7-DN51X5AqiJFWkw6/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
```
 
```
        did:keri:123, oobi    ---------------------------------            ---------------------
   O    ----------------->   |                                 |          |                     |
  -|-   <-----------------   |  dkr did keri resolve           |  <---->  |  KERI WATCHER POOL  |
  / \    diddoc, metadata    |                                 |          |                     |
                              ---------------------------------            ---------------------
```

### `dkr did keri resolver-service`

**Expose did:keri resolver as an HTTP web service.** (Can be deployed as Universal Resolver driver)

Example:
```
dkr did keri resolver-service --name dkr --port 7678
```

```
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dkr did keri resolver-service  |  <---->  |  KERI WATCHER POOL  |
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

### `dkr did webs generate`

**Generate a did:webs DID document and KEL/TEL file.**

Example:
```
dkr did webs generate --name dkr --did did:webs:danubetech.com:example:EPaP4GgZsB6Ww-SeSO2gwNDMNpC7-DN51X5AqiJFWkw6
```

```
                              ---------------------------------
      did.json, keri.cesr    |                                 |
    --------------------->   |  ANY WEB SERVER  /123/did.json  |
   |                         |                  /123/keri.cesr |
   |    UPLOAD                ---------------------------------
   |
   |      
         did:webs:dom:123     ---------------------------------            ---------------------
   O    ----------------->   |                                 |          |                     |
  -|-   <-----------------   |  dkr did webs generate          |  <---->  |  KERI WATCHER POOL  |
  / \   did.json, keri.cesr  |                                 |          |                     |
                              ---------------------------------            ---------------------
```

### `dkr did webs service`

**Launch web server capable of serving KERI AIDs as did:webs and did:web DIDs.**

Example:
```
dkr did webs service --name dkr --port 7677
```

```
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dkr did webs service           |  <---->  |  KERI WATCHER POOL  |
                             |                                 |          |                     |
                              ---------------------------------            ---------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                             /123/keri.cesr |   v  keri.cesr

         did:webs:dom:123     ---------------------------------
   O    ----------------->   |                                 |
  -|-   <-----------------   |  ANY DID:WEBS RESOLVER          |  <-----  (verify did.json/keri.cesr)
  / \    diddoc, metadata    |                                 |
                              ---------------------------------
```

```
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dkr did webs service           |  <---->  |  KERI WATCHER POOL  |
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

### `dkr did webs resolve`

**Resolve a did:webs DID.**

Example:
```
dkr did webs resolve --name dkr --did did:webs:danubetech.com:example:EPaP4GgZsB6Ww-SeSO2gwNDMNpC7-DN51X5AqiJFWkw6
```

```
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dkr did webs service           |  <---->  |  KERI WATCHER POOL  |
                             |                                 |          |                     |
                              ---------------------------------            ---------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                             /123/keri.cesr |   v  keri.cesr

         did:webs:dom:123     ---------------------------------
   O    ----------------->   |                                 |
  -|-   <-----------------   |  dkr did webs resolve           |  <-----  (verify did.json/keri.cesr)
  / \    diddoc, metadata    |                                 |
                              ---------------------------------
```

```
                              ---------------------------------
                             |                                 |
                             |  ANY WEB SERVER  /123/did.json  |
                             |                  /123/keri.cesr |
                              ---------------------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                             /123/keri.cesr |   v  keri.cesr

         did:webs:dom:123     ---------------------------------
   O    ----------------->   |                                 |
  -|-   <-----------------   |  dkr did webs resolve           |  <-----  (verify did.json/keri.cesr)
  / \    diddoc, metadata    |                                 |
                              ---------------------------------
```

```
                              ---------------------------------
                             |                                 |
                             |  ANY WEB SERVER  /123/did.json  |
                             |                  /123/keri.cesr |
                              ---------------------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                                            |   v

         did:web:dom:123     ---------------------------------
   O    ----------------->   |                                 |
  -|-   <-----------------   |  ANY DID:WEB RESOLVER           |
  / \         diddoc         |                                 |
                              ---------------------------------
```

### `dkr did webs resolver-service`

**Expose did:webs resolver as an HTTP web service.** (Can be deployed as Universal Resolver driver)

Example:
```
dkr did keri resolve --name dkr --port 7677
```

```
                              ---------------------------------            ---------------------
                             |                                 |          |                     |
                             |  dkr did webs service           |  <---->  |  KERI WATCHER POOL  |
                             |                                 |          |                     |
                              ---------------------------------            ---------------------
                                            HTTPS
                             HTTP GET       ^   |  200 OK
                             /123/did.json  |   |  did.json
                             /123/keri.cesr |   v  keri.cesr

                              ---------------------------------
                             |                                 |
                             |  dkr did webs resolver-service  |  <-----  (verify did.json/keri.cesr)
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

```
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
                             |  dkr did webs resolver-service  |  <-----  (verify did.json/keri.cesr)
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
