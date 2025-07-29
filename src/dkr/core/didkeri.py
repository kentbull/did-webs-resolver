import json
from typing import List

from hio.base import Doer, doing
from keri.app import habbing

from dkr import log_name, ogler
from dkr.core import didding

logger = ogler.getLogger(log_name)


class KeriResolver(doing.DoDoer):
    """Resolve did:keri DID document from the KEL retrieved during OOBI resolution of the provided OOBI."""

    def __init__(
        self,
        hby: habbing.Habery,
        hby_doer: Doer,
        did: str,
        meta: bool,
        verbose: bool = False,
    ):
        self.hby: habbing.Habery = hby
        self.did: str = did
        self.meta: bool = meta
        self.verbose = verbose

        self.result: dict = {}
        resolve_doer = doing.doify(self.resolve, hby=hby, did=did, meta=meta)
        self.toRemove: List[Doer] = [hby_doer, resolve_doer]
        doers = list(self.toRemove)
        super(KeriResolver, self).__init__(doers=doers)

    def resolve(self, hby: habbing.Habery, did: str, meta: bool, tock=0.0, tymth=None):
        """
        Resolve the did:keri DID document by retrieving the KEL from the OOBI resolution.
        """
        self.wind(tymth)  # prime generator
        self.tock = tock  # prime generator
        yield self.tock  # prime generator

        # Once the OOBI is resolved and the AID's KEL is available in the local Habery then generate the DID artifacts
        try:
            aid = didding.parse_did_keri(did)
            self.result = didding.generate_did_doc(hby, did=did, aid=aid, meta=meta)
            logger.info(f'did:keri Resolution result: {json.dumps(self.result, indent=2)}')
            if self.verbose:
                print(self.result)
                logger.info(f'Resolution result for did:keri DID {self.did}:\n{json.dumps(self.result, indent=2)}')
            logger.info(f'Verification success for did:keri DID: {self.did}')
        except Exception as ex:
            logger.info(f'Verification failure for did:keri DID: {did}: {ex}')
            self.result = {'error': str(ex)}
            print(self.result)
            raise ex
        else:
            self.remove(self.toRemove)
