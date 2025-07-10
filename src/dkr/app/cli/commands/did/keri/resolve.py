# -*- encoding: utf-8 -*-
"""
dkr.app.cli.commands module

"""

import argparse
import json
import logging

from hio.base import doing
from keri.app import habbing, oobiing
from keri.app.cli.common import existing
from keri.db import basing
from keri.help import helping

from dkr import log_name, ogler
from dkr.core import didding

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
    help='Whether to include metadata (True), or only return the DID document (False)',
    type=bool,
    required=False,
    default=None,
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
    ogler.level = logging.getLevelName(args.loglevel.upper())
    logger.setLevel(ogler.level)
    hby = existing.setupHby(name=args.name, base=args.base, bran=args.bran)
    hbyDoer = habbing.HaberyDoer(habery=hby)  # setup doer
    obl = oobiing.Oobiery(hby=hby)
    res = KeriResolver(hby=hby, hbyDoer=hbyDoer, obl=obl, did=args.did, oobi=args.oobi, meta=args.meta)
    return [res]


class KeriResolver(doing.DoDoer):
    """Resolve did:keri DID document from the KEL retrieved during OOBI resolution of the provided OOBI."""

    def __init__(self, hby, hbyDoer, obl, did, oobi, meta):
        self.hby = hby
        self.did = did
        self.oobi = oobi
        self.meta = meta

        self.toRemove = [hbyDoer] + obl.doers
        doers = list(self.toRemove)
        super(KeriResolver, self).__init__(doers=doers)

    def recur(self, tock=0.0, **opts):
        res = self.resolve(tock)
        logger.info(f'did:keri Resolution result: {res}')
        return True

    def resolve(self, tock=0.0):
        aid = didding.parseDIDKeri(self.did)
        logger.error(f'From arguments got aid: {aid}')
        logger.error(f'From arguments got oobi: {self.oobi}')

        obr = basing.OobiRecord(date=helping.nowIso8601())
        obr.cid = aid
        self.hby.db.oobis.pin(keys=(self.oobi,), val=obr)

        while self.hby.db.roobi.get(keys=(self.oobi,)) is None:
            _ = yield tock

        didresult = didding.generateDIDDoc(self.hby, did=self.did, aid=aid, oobi=self.oobi, meta=self.meta)
        dd = didresult[didding.DD_FIELD]
        result = didresult if self.meta else dd
        data = json.dumps(result, indent=2)

        logger.info(f'did:keri Resolution data: {data}')
        self.remove(self.toRemove)
        return result
