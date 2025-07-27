# -*- encoding: utf-8 -*-
"""
dkr.app.cli.commands module

"""

import argparse
import json
from typing import List

from hio.base import Doer, doing
from keri.app import habbing, oobiing
from keri.app.cli.common import existing
from keri.app.habbing import Habery
from keri.vdr.credentialing import Regery

from dkr import log_name, ogler, set_log_level
from dkr.core import artifacting

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

    def __init__(
        self, name: str, base: str, bran: str, did: str, meta: bool = False, verbose: bool = False, output_dir: str = '.'
    ):
        """
        Initializes the did:webs DID file generator.

        Parameters:
            name (str): Name of the controller keystore (Habery) to use for generating the DID document.
            base (str): Base path (namespace for local file tree) for the KERI keystore (Habery) to use for generating the DID document.
            bran (str): Passcode for the controller of the local KERI keystore.
            did (str): The did:webs DID showing the domain and AID to generate the DID document and CESR stream for.
            meta (bool): Whether to include metadata in the DID document generation. Defaults to False.
            verbose (bool): Whether to print the generated DID artifacts at the command line. Defaults to False
            output_dir (str): Directory to output the generated files. Default is current directory.
        """
        self.name: str = name
        self.base: str = base
        self.bran: str = bran
        self.hby: Habery = existing.setupHby(name=name, base=base, bran=bran)
        self.rgy: Regery = Regery(hby=self.hby, name=self.hby.name, base=self.hby.base)
        self.bran: str = bran
        hby_doer = habbing.HaberyDoer(habery=self.hby)  # setup doer
        oobiery = oobiing.Oobiery(hby=self.hby)
        self.did: str = did
        self.meta: bool = meta
        self.verbose: bool = verbose
        self.output_dir: str = output_dir

        self.toRemove: List[Doer] = [hby_doer] + oobiery.doers
        doers = list(self.toRemove)
        super(DIDArtifactGenerator, self).__init__(doers=doers)

    def recur(self, tock=0.0, **opts):
        """DoDoer lifecycle function that calls the underlying DID generation function. Runs once"""
        self.generate_artifacts()
        return True  # run once and then stop

    def generate_artifacts(self):
        """Drive did:webs did.json and keri.cesr generation"""
        logger.debug(f'\nGenerate DID doc for: {self.did}\nand metadata        : {self.meta}')
        did_json, keri_cesr = artifacting.generate_artifacts(self.hby, self.rgy, self.did, self.meta, self.output_dir)

        if self.verbose:
            print(f'keri.cesr:\n{keri_cesr.decode()}\n')
            print(f'did.json:\n{json.dumps(did_json, indent=2)}')
        self.remove(self.toRemove)
        return True
