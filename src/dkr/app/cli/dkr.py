# -*- encoding: utf-8 -*-
"""
kara.app.commands module

"""

import logging

import multicommand
from keri import help
from keri.app import directing

from dkr.app.cli import commands

help.ogler.level = logging.CRITICAL
help.ogler.reopen(name='dkr', temp=True, clear=True)


def main():
    parser = multicommand.create_parser(commands)
    args = parser.parse_args()

    if not hasattr(args, 'handler'):
        parser.print_help()
        return

    try:
        doers = args.handler(args)
        # print(f"doers={doers}")
        directing.runController(doers=doers, expire=0.0)

    except Exception as ex:
        raise ex


if __name__ == '__main__':
    main()
