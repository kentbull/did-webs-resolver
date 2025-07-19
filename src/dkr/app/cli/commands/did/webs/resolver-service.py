# -*- encoding: utf-8 -*-
"""
dkr.app.cli.commands.resolver-service module

"""

import argparse

from keri.app import configing, oobiing

from dkr import log_name, ogler, set_log_level
from dkr.core import habs, resolving

parser = argparse.ArgumentParser(description='Expose did:webs resolver as an HTTP web service')
parser.set_defaults(handler=lambda args: launch(args), transferable=True)
parser.add_argument(
    '-p',
    '--http',
    action='store',
    default=7677,
    help='Port on which to listen for did:webs resolution requests.  Defaults to 7677',
)
parser.add_argument('-n', '--name', action='store', default='dkr', help='Name of controller. Default is dkr.')
parser.add_argument(
    '-b', '--base', required=False, default='', help='additional optional prefix to file location of KERI keystore'
)
# passcode => bran
parser.add_argument(
    '--passcode', dest='bran', default=None, help='22 character encryption passcode for keystore (is not saved)'
)
parser.add_argument('-c', '--config-dir', dest='config_dir', default=None, help='directory override for configuration data')
parser.add_argument('--config-file', dest='config_file', action='store', default=None, help='configuration filename override')
parser.add_argument(
    '--static-files-dir',
    dest='static_files_dir',
    action='store',
    default=None,
    help='static files directory to use for serving the did.json and keri.cesr files. Default is "static"',
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


def launch(args, expire=0.0):
    """
    Launches a Falcon webserver listening on /1.0/identifiers/{did} for did:webs resolution requests
    as a set of Doers
    """
    set_log_level(args.loglevel, logger)
    name = args.name
    base = args.base
    bran = args.bran
    config_file = args.config_file
    config_dir = args.config_dir
    static_files_dir = args.static_files_dir
    http_port = args.http
    keypath = args.keypath
    certpath = args.certpath
    cafilepath = args.cafilepath
    try:
        http_port = int(http_port)
    except ValueError:
        logger.error(f'Invalid port number: {http_port}. Must be an integer.')
        return []

    cf = None
    if config_file is not None:
        cf = configing.Configer(name=config_file, base=base, headDirPath=config_dir, temp=False, reopen=True, clear=False)

    hby, hby_doer = habs.get_habery_doer(name, base, bran, cf)
    oobiery = oobiing.Oobiery(hby=hby)

    doers = [hby_doer] + oobiery.doers
    doers += resolving.setup_resolver(
        hby,
        hby_doer,
        oobiery,
        http_port=http_port,
        static_files_dir=static_files_dir,
        keypath=keypath,
        certpath=certpath,
        cafilepath=cafilepath,
    )

    logger.info(f'Launched did:webs resolver on {http_port}')
    return doers
