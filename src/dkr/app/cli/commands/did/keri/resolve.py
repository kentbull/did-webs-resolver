# -*- encoding: utf-8 -*-
"""
dkr.app.cli.commands module

"""

import argparse

from keri.app import habbing, oobiing
from keri.app.cli.common import existing

from dkr import log_name, ogler, set_log_level
from dkr.core.didkeri import KeriResolver

parser = argparse.ArgumentParser(description='Resolve a did:keri DID')
parser.set_defaults(handler=lambda args: handler(args), transferable=True)
parser.add_argument('-n', '--name', action='store', default='dkr', help='Name of controller. Default is dkr.')
parser.add_argument(
    '--base', '-b', help='additional optional prefix to file location of KERI keystore', required=False, default=''
)
parser.add_argument(
    '--passcode', help='22 character encryption passcode for keystore (is not saved)', dest='bran', default=None
)  # passcode => bran
parser.add_argument('--did', '-d', help='DID to resolve (did:keri method)', required=True)
parser.add_argument('--oobi', '-o', help='OOBI to use for resolving the DID', required=False)
parser.add_argument(
    '--meta',
    '-m',
    help='Whether to include metadata or only return the DID document',
    action='store_true',
    required=False,
    default=False,
)
parser.add_argument(
    '-v',
    '--verbose',
    action='store_true',
    required=False,
    default=False,
    help='Show the verbose output of DID resolution',
)
parser.add_argument(
    '--loglevel',
    action='store',
    required=False,
    default='CRITICAL',
    help='Set log level to DEBUG | INFO | WARNING | ERROR | CRITICAL. Default is CRITICAL',
)

logger = ogler.getLogger(log_name)


def handler(args):
    """Creates the list of doers that handles command line did:keri DID doc resolutions"""
    set_log_level(args.loglevel, logger)
    hby = existing.setupHby(name=args.name, base=args.base, bran=args.bran)
    hby_doer = habbing.HaberyDoer(habery=hby)  # setup doer
    oobiery = oobiing.Oobiery(hby=hby)
    res = KeriResolver(
        hby=hby, hby_doer=hby_doer, oobiery=oobiery, did=args.did, oobi=args.oobi, meta=args.meta, verbose=args.verbose
    )
    return [res]
