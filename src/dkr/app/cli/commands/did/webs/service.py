# -*- encoding: utf-8 -*-
"""
dkr.app.cli.commands module

"""

import argparse
from typing import List

from hio.base import Doer
from keri.app import oobiing
from keri.vdr import credentialing

from dkr import log_name, ogler, set_log_level
from dkr.core import artifacting, habs

parser = argparse.ArgumentParser(description='Launch web server capable of serving KERI AIDs as did:webs and did:web DIDs')
parser.set_defaults(handler=lambda args: launch(args), transferable=True)
parser.add_argument(
    '-d',
    '--did-path',
    action='store',
    default='',
    help="did:webs path segment in URL format between {host}%3A{port} and {aid}. Example: 'somepath/somesubpath'",
)
parser.add_argument('-p', '--http', action='store', default=7676, help='Port on which to listen for did:webs requests')
parser.add_argument('-n', '--name', action='store', required=True, help='Name of controller.')
parser.add_argument('-a', '--alias', action='store', required=True, help='Alias of controller.')
parser.add_argument(
    '--base', '-b', help='additional optional prefix to file location of KERI keystore', required=False, default=''
)
parser.add_argument(
    '--passcode', help='22 character encryption passcode for keystore (is not saved)', dest='bran', default=None
)  # passcode => bran
parser.add_argument('--config-dir', '-c', dest='config_dir', help='directory override for configuration data', default=None)
parser.add_argument('--config-file', dest='config_file', action='store', help='configuration filename override')
parser.add_argument(
    '-m',
    '--meta',
    action='store_true',
    required=False,
    default=False,
    help='Whether to include metadata (True), or only return the DID document (False)',
)
parser.add_argument('--keypath', action='store', required=False, default=None)
parser.add_argument('--certpath', action='store', required=False, default=None)
parser.add_argument('--cafilepath', action='store', required=False, default=None)
parser.add_argument(
    '--loglevel',
    action='store',
    required=False,
    default='CRITICAL',
    help='Set log level to DEBUG | INFO | WARNING | ERROR | CRITICAL. Default is CRITICAL',
)

logger = ogler.getLogger(log_name)


def launch(args):
    """Handle CLI command for serving did:webs artifacts."""
    set_log_level(args.loglevel, logger)
    http_port = args.http
    try:
        http_port = int(http_port)
    except ValueError:
        logger.error(f'Invalid port number: {http_port}. Must be an integer.')
        raise

    logger.info(f'Launched did:webs artifact webserver: {http_port}')
    return create_artifact_server_doers(
        name=args.name,
        base=args.base,
        bran=args.bran,
        config_file=args.config_file,
        config_dir=args.config_dir,
        alias=args.alias,
        meta=args.meta,
        did_path=args.did_path,
        http_port=http_port,
        keypath=args.keypath,
        certpath=args.certpath,
        cafilepath=args.cafilepath,
    )


def create_artifact_server_doers(
    name: str,
    base: str,
    bran: str,
    config_file: str,
    config_dir: str,
    alias: str,
    meta: bool,
    did_path: str,
    http_port: int,
    keypath: str = None,
    certpath: str = None,
    cafilepath: str = None,
) -> List[Doer]:
    """Create a list of Doers for serving did:webs artifacts."""
    cf = habs.get_habery_configer(name=config_file, base=base, head_dir_path=config_dir)
    hby, hby_doer = habs.get_habery_and_doer(name, base, bran, cf)
    rgy = credentialing.Regery(hby=hby, name=hby.name, base=hby.base, temp=hby.temp)
    oobiery = oobiing.Oobiery(hby=hby)
    doers = oobiery.doers + [hby_doer]

    doers += artifacting.dyn_artifact_svr_doers(
        hby=hby,
        rgy=rgy,
        alias=alias,
        http_port=http_port,
        did_path=did_path,
        meta=meta,
        keypath=keypath,
        certpath=certpath,
        cafilepath=cafilepath,
    )

    return doers
