import json
from typing import List

from hio.base import Doer, doing
from keri.app import configing, habbing
from keri.vdr import credentialing

from dkr import log_name, ogler
from dkr.core import didding, habs

logger = ogler.getLogger(log_name)


class KeriResolver(doing.DoDoer):
    """Resolve did:keri DID document from the KEL retrieved during OOBI resolution of the provided OOBI."""

    def __init__(
        self,
        did: str,
        meta: bool = False,
        verbose: bool = False,
        hby: habbing.Habery | None = None,
        rgy: credentialing.Regery | None = None,
        cf: configing.Configer | None = None,
        name: str | None = None,
        base: str | None = None,
        bran: str | None = None,
        config_file: str | None = None,
        config_dir: str | None = None,
    ):
        """
        Initializes the set of Doers needed to resolve a did:keri DID document based on the KEL of
        the embedded AID.

        Parameters:
            name: Name of the Habery.
            base: Base directory for the Habery.
            bran: Passcode for the Habery (optional).
            config_file: Habery configuration file name (optional).
            config_dir: Directory for Habery configuration data (optional).
            did: The did:keri DID to resolve.
            meta: Whether to include metadata in the resolution result.
            verbose: Whether to print verbose output.
            hby: Existing Habery instance (optional).
            rgy: Existing Regery instance (optional).
            cf: Configurationer instance (optional).
        """
        cf = cf if cf else habs.get_habery_configer(name=config_file, base=base, head_dir_path=config_dir)
        if hby is None:
            hby, hby_doer = habs.get_habery_and_doer(name, base, bran, cf)
        else:
            hby_doer = habbing.HaberyDoer(habery=hby)
        self.hby: habbing.Habery = hby
        self.rgy = (
            rgy if rgy else credentialing.Regery(hby=self.hby, name=self.hby.name, base=self.hby.base, temp=self.hby.temp)
        )
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
            self.result = didding.generate_did_doc(hby, rgy=self.rgy, did=did, aid=aid, meta=meta)
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
