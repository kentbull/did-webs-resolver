import json
import os

import falcon
from keri.app import habbing

from dkr.core import didding

DID_JSON = 'did.json'


class DIDWebsResourceEnd:
    """
    did.json HTTP resource for accessing did:webs DID documents for KERI AIDs.
    """

    def __init__(self, hby: habbing.Habery, meta: bool = False):
        """
        Initialize did:webs did.json artifact endpoint that will pull designated aliases from the specified registry
        and will optionally include metadata in the DID document.

        Parameters:
            hby (Habery): Database environment for AIDs to expose
            meta (bool): Whether to include metadata in the DID document. Default is False.
        """
        self.hby = hby
        self.meta = meta
        super().__init__()

    def on_get(self, req, rep, aid):
        """GET endpoint for resolving KERI AIDs as did:web DIDs

        Parameters:
            req (Request) Falcon HTTP Request object:
            rep (Response) Falcon HTTP Response object:
            aid (str): AID to resolve, or path used if None
        """
        # Read the DID from the parameter extracted from path or manually extract
        if not req.path.endswith(f'/{DID_JSON}'):
            raise falcon.HTTPBadRequest(description=f'invalid did:web DID URL {req.path}')

        if aid is None:
            aid = os.path.basename(os.path.normpath(req.path.replace(f'/{DID_JSON}', '')))

        # 404 if AID not recognized
        if aid not in self.hby.kevers:
            raise falcon.HTTPNotFound(description=f'KERI AID {aid} not found')

        path = os.path.normpath(req.path).replace(f'/{DID_JSON}', '').replace('/', ':')
        port = ''
        if req.port != 80 and req.port != 443:
            port = f'%3A{req.port}'

        did = f'did:web:{req.host}{port}{path}'

        # Generate the DID Doc and return
        diddoc = didding.generate_did_doc(self.hby, did, aid, meta=self.meta)

        rep.status = falcon.HTTP_200
        rep.content_type = 'application/json'
        rep.data = json.dumps(diddoc, indent=2).encode('utf-8')
