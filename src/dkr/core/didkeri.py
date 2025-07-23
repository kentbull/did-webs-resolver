import json
from typing import List

from hio.base import Doer, doing
from keri.app import habbing, oobiing
from keri.db import basing
from keri.help import helping

from dkr import log_name, ogler
from dkr.core import didding

logger = ogler.getLogger(log_name)


class KeriResolver(doing.DoDoer):
    """Resolve did:keri DID document from the KEL retrieved during OOBI resolution of the provided OOBI."""

    def __init__(
        self,
        hby: habbing.Habery,
        hby_doer: Doer,
        oobiery: oobiing.Oobiery,
        did: str,
        oobi: str,
        meta: bool,
        verbose: bool = False,
    ):
        self.hby: habbing.Habery = hby
        self.did: str = did
        self.oobi: str = oobi
        self.meta: bool = meta
        self.verbose = verbose

        self.result: dict = {}
        resolve_doer = doing.doify(self.resolve, hby=hby, did=did, oobi=oobi, meta=meta)
        self.toRemove: List[Doer] = [hby_doer, resolve_doer] + oobiery.doers
        doers = list(self.toRemove)
        super(KeriResolver, self).__init__(doers=doers)

    def resolve_oobi(self, aid: str, oobi: str, tock=0.0):
        # Resolve provided OOBI to get the KEL of the AID passed in
        obr = basing.OobiRecord(date=helping.nowIso8601())
        obr.cid = aid
        self.hby.db.oobis.pin(keys=(oobi,), val=obr)

        while self.hby.db.roobi.get(keys=(oobi,)) is None:
            _ = yield tock

    def resolve(self, hby: habbing.Habery, did: str, oobi: str, meta: bool, tock=0.0, tymth=None):
        """
        Resolve the did:keri DID document by retrieving the KEL from the OOBI resolution.
        """
        self.wind(tymth)  # prime generator
        self.tock = tock  # prime generator
        yield self.tock  # prime generator

        aid = didding.parse_did_keri(did)

        # Resolve provided OOBI to get the KEL of the AID passed in
        self.resolve_oobi(aid=aid, oobi=oobi, tock=tock)

        # Once the OOBI is resolved and the AID's KEL is available in the local Habery then generate the DID artifacts
        try:
            self.result = didding.generate_did_doc(hby, did=did, aid=aid, oobi=oobi, meta=meta)
            logger.info(f'did:keri Resolution result: {json.dumps(self.result, indent=2)}')
            if self.verbose:
                print(self.result)
                logger.info(f'Resolution result for did:keri DID {self.did}:\n{json.dumps(self.result, indent=2)}')
            logger.info(f'Verification success for did:keri DID: {self.did}')
        except Exception as ex:
            logger.error(f'Error resolving did:keri DID: {did} with OOBI {oobi}: {ex}')
            logger.info(f'Verification failure for did:keri DID: {did} with OOBI {oobi}: {ex}')
            self.result = {'error': str(ex)}
            print(self.result)
        else:
            self.remove(self.toRemove)
