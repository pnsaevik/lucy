"""
A collection of tools related to salmon lice research at IMR
"""


__version__ = "1.1.0"

import re

"""
Package version
"""


def run(*argv):
    func, kwargs = _get_func_and_params(*argv)
    if func is None:
        return
    else:
        func(**kwargs)


def main(*argv):
    import sys
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    if len(argv) == 0:
        argv = sys.argv[1:]
    run(*argv)


def _get_func_and_params(*argv):
    import argparse
    from . import tools
    import inspect

    subcommands = {
        'licebiomass': tools.make_licebiomass,
    }

    # Create the top-level parser
    parser = argparse.ArgumentParser(
        prog='lucy',
        description="Command-line tools related to salmon lice research at IMR",
        epilog="Use 'lucy <subcommand> -h' for more information on a specific subcommand.",
    )

    # Create the subparsers object
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # Create the parser for individual commands
    for cmd_name, func in subcommands.items():
        s = inspect.signature(func)
        d = inspect.getdoc(func)
        first_line = d.split(sep='\n', maxsplit=1)[0]
        descr = d.split(sep=':param', maxsplit=1)[0]
        p = subparsers.add_parser(
            name=cmd_name,
            help=first_line,
            description=descr,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        pattern = re.compile(
            r':param ([^:]+):(.+?)(?=:param|:return|$)',
            flags=re.DOTALL,
        )
        pat_descr = dict(pattern.findall(d))
        for param_name, param in s.parameters.items():
            param_spec = param_name
            if param.default is not inspect.Parameter.empty:
                param_spec = '--' + param_spec
            p.add_argument(param_spec, help=pat_descr[param_name])

    # Parse the arguments
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return None, dict()

    # Call the function
    funcname = args.command
    func = subcommands[funcname]
    kwargs = {}
    for k, v in vars(args).items():
        if k == 'command':
            continue
        if v is None:
            continue
        kwargs[k] = v

    return func, kwargs
