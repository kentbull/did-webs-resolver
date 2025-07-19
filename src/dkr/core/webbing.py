# -*- encoding: utf-8 -*-
"""
dkr.core.webbing module

"""

import falcon
from keri.app import habbing

from dkr.core import ends


def load_endpoints(app: falcon.App, hby: habbing.Habery, did_path: str = '', meta: bool = False) -> None:
    """
    Set up web app endpoints to serve configured KERI AIDs as `did:web` DIDs

    Parameters:
        app (App): Falcon app to register endpoints against
        hby (Habery): Database environment for exposed KERI AIDs
        did_path (str): Optional prefixed path segment to include in the URL for did:webs. Defaults to empty string.
        meta (bool): Whether to include metadata in the DID document. Default is False.
    """
    app.add_route('/health', ends.HealthEnd())
    did_webs_path = '' if not did_path else f'/{did_path}'
    app.add_route(f'{did_webs_path}/{{aid}}/did.json', ends.DIDWebsResourceEnd(hby, meta=meta))
    app.add_route(f'{did_webs_path}/{{aid}}/keri.cesr', ends.KeriCesrResourceEnd(hby))
