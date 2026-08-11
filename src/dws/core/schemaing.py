# -*- encoding: utf-8 -*-
"""
dws.core.schemaing module

Helpers for pinning schemas the resolver must know before parsing ACDCs.
"""

import json
from importlib import resources

from keri import kering
from keri.app import habbing
from keri.core import scheming

from dws.core import didding

RESOURCE_PACKAGE = 'dws.resources'
DES_ALIASES_PUBLIC_SCHEMA_FILE = 'designated-aliases-public-schema.json'


def load_designated_aliases_schema() -> dict:
    """Load the embedded public designated-alias ACDC schema."""
    schema_file = resources.files(RESOURCE_PACKAGE).joinpath(DES_ALIASES_PUBLIC_SCHEMA_FILE)
    return json.loads(schema_file.read_text(encoding='utf-8'))


def pin_designated_aliases_schema(hby: habbing.Habery):
    """Pin the embedded public designated-alias schema into a Habery."""
    schemer = hby.db.schema.get(keys=(didding.DES_ALIASES_SCHEMA,))
    if schemer is not None:
        return schemer

    schemer = scheming.Schemer(sed=load_designated_aliases_schema())
    if schemer.said != didding.DES_ALIASES_SCHEMA:
        raise kering.ConfigurationError(f'embedded designated-alias schema SAID mismatch: {schemer.said}')

    hby.db.schema.pin(schemer.said, schemer)
    return schemer
