# -*- encoding: utf-8 -*-
"""
dkr.app.cli.commands module

"""

import argparse
import json

from hio.base import doing
from keri.app import habbing, oobiing
from keri.app.cli.common import existing
from keri.vdr import credentialing

from dkr import log_name, ogler, set_log_level
from dkr.core import artifacting, didding

parser = argparse.ArgumentParser(description='Generate a did:webs DID document and KEL, TEL, and ACDC CESR stream file')
parser.set_defaults(handler=lambda args: handler(args), transferable=True)
parser.add_argument('-n', '--name', action='store', default='dkr', help='Name of controller. Default is dkr.')
parser.add_argument(
    '-b', '--base', required=False, default='', help='additional optional prefix to file location of KERI keystore'
)
parser.add_argument(
    '-p', '--passcode', dest='bran', default=None, help='22 character encryption passcode for keystore (is not saved)'
)  # passcode => bran
parser.add_argument(
    '--output-dir',
    required=False,
    default='.',
    help='Directory to output the generated files. Default is current directory.',
)
parser.add_argument(
    '-o',
    '--oobi',
    required=False,
    default=None,
    help='OOBI to use for resolving the AID',
)
parser.add_argument(
    '-m',
    '--meta',
    action='store_true',
    required=False,
    default=False,
    help='Whether to include metadata (True), or only return the DID document (False)',
)
parser.add_argument('-d', '--did', required=True, help='DID to generate (did:webs method)')
parser.add_argument(
    '-v',
    '--verbose',
    action='store_true',
    required=False,
    default=False,
    help='Show the verbose output of DID generation artifacts.',
)
parser.add_argument(
    '--loglevel',
    action='store',
    required=False,
    default='CRITICAL',
    help='Set log level to DEBUG | INFO | WARNING | ERROR | CRITICAL. Default is CRITICAL',
)

logger = ogler.getLogger(log_name)


def handler(args: argparse.Namespace) -> list[doing.Doer]:
    """
    Perform did:webs artifact generation for the DID document and keri.cesr CESR stream and then shut down.
    """
    set_log_level(args.loglevel, logger)
    gen = DIDArtifactGenerator(
        name=args.name,
        base=args.base,
        bran=args.bran,
        did=args.did,
        oobi=args.oobi,
        meta=args.meta,
        verbose=args.verbose,
        output_dir=args.output_dir,
    )
    return [gen]


class DIDArtifactGenerator(doing.DoDoer):
    """
    Generates a did:webs DID document and the associated CESR stream for the {AID}.json and keri.cesr files.
    - {AID}.json contains the DID document
    - keri.cesr contains the CESR event stream for the KELs, TELs, and ACDCs associated with the DID.
    """

    def __init__(self, name, base, bran, did, oobi, meta=False, verbose=False, output_dir='.'):
        """
        Initializes the did:webs DID file generator.

        Parameters:
            name (str): Name of the controller keystore (Habery) to use for generating the DID document.
            base (str): Base path (namespace for local file tree) for the KERI keystore (Habery) to use for generating the DID document.
            bran (str): Passcode for the controller of the local KERI keystore.
            did (str): The did:webs DID showing the domain and AID to generate the DID document and CESR stream for.
            oobi (str): OOBI to use for resolving the AID (not currently used).
            meta (bool): Whether to include metadata in the DID document generation. Defaults to False.
            verbose (bool): Whether to print the generated DID artifacts at the command line. Defaults to False
            output_dir (str): Directory to output the generated files. Default is current directory.
        """
        self.name = name
        self.base = base
        self.bran = bran
        self.hby = existing.setupHby(name=name, base=base, bran=bran)
        self.rgy = credentialing.Regery(hby=self.hby, name=self.hby.name, base=self.hby.base)
        self.bran = bran
        hby_doer = habbing.HaberyDoer(habery=self.hby)  # setup doer
        oobiery = oobiing.Oobiery(hby=self.hby)
        self.did = did
        self.oobi = oobi
        self.meta = meta
        self.verbose = verbose
        self.output_dir = output_dir

        self.toRemove = [hby_doer] + oobiery.doers
        doers = list(self.toRemove)
        super(DIDArtifactGenerator, self).__init__(doers=doers)

    def recur(self, tock=0.0, **opts):
        """DoDoer lifecycle function that calls the underlying DID generation function. Runs once"""
        self.generate_artifacts()
        return True  # run once and then stop

    def generate_artifacts(self):
        """Drive did:webs did.json and keri.cesr generation"""
        logger.debug(
            f'\nGenerate DID doc for: {self.did}'
            f'\nusing OOBI          : {self.oobi}'
            f'\nand metadata        : {self.meta}'
        )
        domain, port, path, aid = didding.parse_did_webs(self.did)

        logger.info(f'Generating CESR event stream data from local Habery keystore')
        hab = self.hby.habs[aid]
        reger = self.rgy.reger
        keri_cesr = bytearray()
        # self.retrieve_kel_via_oobi() # not currently used; an alternative to relying on a local KEL keystore
        keri_cesr.extend(artifacting.gen_kel_cesr(self.hby.db, aid))  # add KEL CESR stream
        keri_cesr.extend(artifacting.gen_des_aliases_cesr(hab, reger, aid))  # add designated aliases TELs and ACDCs
        artifacting.write_keri_cesr_file(self.output_dir, aid, keri_cesr)

        # generate did doc
        diddoc = didding.generate_did_doc(self.hby, did=self.did, aid=aid, oobi=None, meta=self.meta)
        if diddoc is None:
            logger.error('DID document failed to generate')
            self.remove(self.toRemove)
            return None

        # Create the directory (and any intermediate directories in the given path) if it doesn't already exist
        dd_dir_path = artifacting.make_did_json_path(self.output_dir, aid)
        artifacting.write_did_json_file(dd_dir_path, diddoc, self.meta)

        if self.verbose:
            print(f'keri.cesr:\n{keri_cesr.decode()}\n')
            print(f'did.json:\n{json.dumps(diddoc, indent=2)}')
        self.remove(self.toRemove)
        return True
