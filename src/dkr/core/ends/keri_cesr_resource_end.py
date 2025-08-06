# -*- encoding: utf-8 -*-
"""
dkr.core.webbing module

"""

import falcon
from keri.app import habbing
from keri.app.habbing import Hab, Habery
from keri.vdr import credentialing
from keri.vdr.viring import Reger

from dkr.core import artifacting

KERI_CESR = 'keri.cesr'
CESR_MIME = 'application/cesr'


class KeriCesrResourceEnd:
    """
    keri.cesr resource endpoint for accessing all KEL, TEL, and ACDC artifacts needed for did:webs DIDs
    """

    def __init__(self, hby: habbing.Habery, rgy: credentialing.Regery):
        """
        Initialize did:webs keri.cesr artifact endpoint that will pull designated aliases from the specified registry.

        Parameters:
            hby (Habery): Database environment for AIDs to expose
            rgy (Regery): Registry for credential and registry data
        """
        self.hby: habbing.Habery = hby
        self.rgy: credentialing.Regery = rgy

    def on_get(self, req, rep, aid):
        """GET endpoint for accessing {KERI_CESR} stream for AID

        Parameters:
            req (Request) Falcon HTTP Request object:
            rep (Response) Falcon HTTP Response object:
            aid (str): AID to access {KERI_CESR} stream for
        """
        # Read the DID from the parameter extracted from path or manually extract
        if not req.path.endswith(f'/{KERI_CESR}'):
            raise falcon.HTTPBadRequest(description=f'invalid {KERI_CESR} DID URL {req.path}')

        if aid not in self.hby.kevers:
            raise falcon.HTTPNotFound(description=f'KERI AID {aid} not found')

        hab = self.hby.habs[aid]
        keri_cesr = gen_keri_cesr(hab, self.rgy.reger, aid)

        rep.status = falcon.HTTP_200
        rep.content_type = CESR_MIME
        rep.data = keri_cesr


def gen_keri_cesr(hab: Hab, reger: Reger, aid: str) -> bytearray:
    """Load KEL, TEL, and ACDC CESR bytes for the givne AID."""
    keri_cesr = bytearray()
    keri_cesr.extend(artifacting.gen_kel_cesr(hab, pre=aid))  # add KEL CESR stream
    keri_cesr.extend(artifacting.gen_loc_schemes_cesr(hab, aid))
    keri_cesr.extend(artifacting.gen_des_aliases_cesr(hab, reger, aid))  # add designated aliases TELs and ACDCs
    return keri_cesr
