# -*- encoding: utf-8 -*-
"""
dkr.app.cli.commands module

"""

import argparse

import viking
from hio.core import http
from keri.app import oobiing
from keri.vdr import credentialing

from dkr import log_name, ogler, set_log_level
from dkr.core import habs, resolving, webbing

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
    """Create list of Doers for serving did:webs artifacts."""
    set_log_level(args.loglevel, logger)
    name = args.name
    alias = args.alias
    base = args.base
    bran = args.bran
    config_file = args.config_file
    config_dir = args.config_dir
    http_port = args.http
    keypath = args.keypath
    certpath = args.certpath
    cafilepath = args.cafilepath
    try:
        http_port = int(http_port)
    except ValueError:
        logger.error(f'Invalid port number: {http_port}. Must be an integer.')
        return []

    did_path = args.did_path
    meta = args.meta

    cf = habs.get_habery_configer(name=config_file, base=base, head_dir_path=config_dir)
    hby, hby_doer = habs.get_habery_and_doer(name, base, bran, cf)
    rgy = credentialing.Regery(hby=hby, name=hby.name, base=hby.base, temp=hby.temp)

    app = resolving.falcon_app()
    webbing.load_endpoints(app, hby=hby, rgy=rgy, did_path=did_path, meta=meta)

    oobiery = oobiing.Oobiery(hby=hby)
    voodoers = viking.setup(hby=hby, alias=alias)
    server = resolving.tls_falcon_server(app, http_port, keypath, certpath, cafilepath)
    http_server_doer = http.ServerDoer(server=server)
    doers = oobiery.doers + [hby_doer, http_server_doer]
    doers.extend(voodoers)

    logger.info(f'Launched did:webs artifact webserver: {http_port}')
    return doers
