import argparse

from hio.base import doing

import dkr

def create_parser() -> argparse.ArgumentParser:
    """
    Create and return the argument parser for the version command.
    """
    parser = argparse.ArgumentParser(description='Print version of did:webs resolver')
    parser.set_defaults(handler=lambda args: handler(args))
    parser.add_argument('--verbose', '-v', help='verbose version information', required=False, default=False, action="store_true")
    return parser

parser = create_parser()

def handler(args: argparse.Namespace) -> list[doing.Doer]:
    kwa = dict(args=args)
    return [doing.doify(version, **kwa)]

def version(tymth, tock=0.0, existing=None, **opts):
    """Prints the version of the library"""
    _ = (yield tock)
    args = opts["args"]
    verbose = args.verbose
    if not verbose:
        print(f"{dkr.__version__}")
    else:
        print(f"did:webs resolver version: {dkr.__version__}")