FROM gleif/dws-base:latest
# This image runs the did:webs and did:keri resolver. The local controller AID does not matter
# very much as it is only used to run the local keystore, not to sign anything.
# the "dkr" keystore can be replaced with any other name, yet it must match the name of the
# config file at /dws/config/<config_file_name>.json

EXPOSE 7677

WORKDIR /dws

# Default resolver run command
CMD ["dkr", "did", "webs", "resolver-service", \
    "--http", "7677", \
    "--name", "dkr", \
    "--config-dir", "/dws/config", \
    "--config-file", "dkr.json", \
    "--loglevel", "INFO" \
    ]