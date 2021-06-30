#!/usr/bin/python3

from . import utils

def generate_markdown(parser, program_name=None):
    if program_name is None:
        program_name = parser.prog

    r = ''

    if hasattr(parser, 'markdown_prolog'):
        r += parser.markdown_prolog

    if parser.description:
        r += 'DESCRIPTION\n'
        r += '-----------\n\n'
        r += parser.description + '\n'
    r += '\n'

    r += 'SYNOPSIS\n'
    r += '--------\n\n'

    if parser.usage:
        r += parser.usage + '\n'
    else:
        r += f'`{program_name}` [OPTIONS]\n\n'

    if parser._actions:
        r += 'OPTIONS\n'
        r += '-------\n\n'

    for a in parser._actions:
        typ = a.type or str
        typ = utils.type2str(typ)
        r += '  `' + ', '.join(a.option_strings)
        if a.metavar:
            r += f" {a.metavar}"
        if a.choices:
            r += ' [%s]' % ', '.join(map(str, utils.limit_choices(a.choices)))
        elif a.takes_args() and not a.metavar:
            r += f' {typ}'
        r += '`\n'
        r += '    %s\n\n' % a.help

    subparsers = parser.get_subparsers()
    if len(subparsers):
        r += '\nCOMMANDS\n'
        r += '---------\n\n'
        r += '%s\n' % ', '.join(subparsers.keys())
        for name, sub in subparsers.items():
            sub.prog = name
            r += '\n%s\n' % generate_markdown(sub)

    if parser.epilog:
        r += parser.epilog

    if hasattr(parser, 'markdown_epilog'):
        r += parser.markdown_epilog

    return r

