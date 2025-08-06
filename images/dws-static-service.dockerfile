FROM gleif/dws-base:latest
# This image runs the did:webs and did:keri resolver as a static web asset host of did.json and keri.cesr files.
# The local controller AID does not matter as it is only used to run the static webserver.
# the "dkr" keystore can be replaced with any other name.

EXPOSE 7676

WORKDIR /dws

# Default resolver run command as a static web host.
# make sure to set the `--did-path` argument, if used, to the path components in your did:webs DIDs
# e.g. `did:webs:example.com:alice:has:friends:EBFn5ge82EQwxp9eeje-UMEXF-v-3dlfbdVMX_PNjSft`
# would have a `--did-path` of `alice/has/friends`.
# Note the absence of the leading and trailing slash '/' characters.
CMD ["dkr", "did", "webs", "resolver-service", \
    "--http", "7676", \
    "--name", "dkr", \
    "--config-dir", "/dws/config", \
    "--config-file", "dkr.json", \
    "--static-files-dir", "/dws/web", \
    "--loglevel", "INFO" \
    ]