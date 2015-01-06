from __future__ import print_function
import sys
import argparse
import inspect

from devkb.utils import walk_modules
from devkb.command import BaseCommand


def _get_commands_from_module(module):
    d = {}
    for cmdclass in _iter_command_classes(module):
        cmd = cmdclass()
        d[cmd.name()] = cmd
    return d


def _iter_command_classes(module_name):
    # TODO: add `name` attribute to commands and and merge this function with
    # scrapy.utils.spider.iter_spider_classes
    for module in walk_modules(module_name):
        for obj in vars(module).itervalues():
            if inspect.isclass(obj) and \
               issubclass(obj, BaseCommand) and \
               obj.__module__ == module.__name__:
                yield obj


def execute(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    cmds = _get_commands_from_module('devkb.commands')
    parser = argparse.ArgumentParser(
        description='Developer Knowledge Database Mining')
    subparsers = parser.add_subparsers(
        title='subcommands:', help='list valid subcommands here')
    for name, cmd in cmds.items():
        _subparser = subparsers.add_parser(name, help=cmd.help())
        _subparser.set_defaults(func=cmd.run)
        cmd.add_arguments(_subparser)

    args = parser.parse_args(sys.argv[1:])
    args.func(args)
