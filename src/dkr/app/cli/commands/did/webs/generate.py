# -*- encoding: utf-8 -*-
"""
dkr.app.cli.commands module

"""

import argparse

from hio.base import doing

from dkr import log_name, ogler, set_log_level
from dkr.core.generating import DIDArtifactGenerator

parser = argparse.ArgumentParser(description='Generate a did:webs DID document and KEL, TEL, and ACDC CESR stream file')
parser.set_defaults(handler=lambda args: handler(args), transferable=True)
parser.add_argument('-n', '--name', action='store', required=True, help='Name of controller.')
parser.add_argument(
    '-b', '--base', required=False, default='', help='additional optional prefix to file location of KERI keystore'
)
# passcode => bran
parser.add_argument(
    '-p', '--passcode', dest='bran', default=None, help='22 character encryption passcode for keystore (is not saved)'
)
parser.add_argument('--config-dir', '-c', dest='config_dir', help='directory override for configuration data', default=None)
parser.add_argument('--config-file', dest='config_file', action='store', default=None, help='configuration filename override')
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
    Return a list of HIO Doers that perform did:webs artifact generation for the DID document and
    keri.cesr CESR stream and then shut down.
    """
    set_log_level(args.loglevel, logger)
    return [
        DIDArtifactGenerator(
            name=args.name,
            base=args.base,
            bran=args.bran,
            config_dir=args.config_dir,
            config_file=args.config_file,
            did=args.did,
            meta=args.meta,
            output_dir=args.output_dir,
            verbose=args.verbose,
        )
    ]
