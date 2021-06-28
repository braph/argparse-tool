#!/usr/bin/python3

from . import utils

def generate_markdown(p, prog=None):
    if prog is None:
        prog = p.prog

    r = ''

    if hasattr(p, 'markdown_prolog'):
        r += p.markdown_prolog

    if p.description:
        r += 'DESCRIPTION\n'
        r += '-----------\n\n'
        r += p.description + '\n'
    r += '\n'

    r += 'SYNOPSIS\n'
    r += '--------\n\n'

    if p.usage:
        r += p.usage + '\n'
    else:
        r += f'`{prog}` [OPTIONS]\n\n'

    if p._actions:
        r += 'OPTIONS\n'
        r += '-------\n\n'

    for a in p._actions:
        typ = a.type or str
        typ = utils.type2str(typ)
        r += f"  `{', '.join(a.option_strings)}"
        if a.metavar:
            r += f" {a.metavar}"
        if a.choices:
            r += ' [%s]' % ', '.join(map(str, utils.limit_choices(a.choices)))
        elif a.takes_args() and not a.metavar:
            r += f' {typ}'
        r += '`\n'
        r += '    %s\n\n' % a.help

    subparsers = p.get_subparsers()
    if len(subparsers):
        r += '\nCOMMANDS\n'
        r += '---------\n\n'
        r += '%s\n' % ', '.join(subparsers.keys())
        for name, sub in subparsers.items():
            sub.prog = name
            r += '\n%s\n' % generate_markdown(sub)

    if p.epilog:
        r += p.epilog

    if hasattr(p, 'markdown_epilog'):
        r += p.markdown_epilog

    return r

