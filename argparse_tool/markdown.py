#!/usr/bin/python3

import argparse
from . import utils

def escape_underscore(s):
    return s.replace('_', '\\_')

def generate_option(action):
    r = ''

    if action.option_strings:
        r += '_%s_' % ', '.join(escape_underscore(a) for a in action.option_strings)

    metavar = action.get_metavar()
    if metavar:
        r += " **%s**" % escape_underscore(metavar)

    if action.choices:
        r += ' [_%s_]' % ', '.join(escape_underscore(str(c)) for c in utils.limit_choices(action.choices))

    return r

def generate_usage(parser, program_name):
    r = ''
    r += f'**{program_name}** [_OPTIONS_]'
    for a in parser.get_positionals():
        if a.dest != argparse.SUPPRESS: # TODO?
            r += ' **%s**' % a.dest
    return r


def heading(string, level):
    return ('#' * level) + ' ' + string + '\n'

def generate_parser(parser, program_name, level=1):
    subparsers = parser.get_subparsers()
    r = ''

    if hasattr(parser, 'markdown_prolog'):
        r += parser.markdown_prolog

    if parser.description:
        r += heading('DESCRIPTION', level)
        r += parser.description + '\n'
    r += '\n'

    r += heading('SYNOPSIS', level)

    if parser.usage:
        r += parser.usage + '\n'
    else:
        r += generate_usage(parser, program_name) + '\n\n'

    if parser._actions:
        r += heading('OPTIONS', level)
        r += '\n'

    # Positionals first
    for a in parser.get_positionals():
        r += '  ' + generate_option(a) + '\n'
        r += '    %s\n\n' % (a.help if a.help else '')

    # Options second
    for a in parser.get_options():
        r += '  ' + generate_option(a) + '\n'
        r += '    %s\n\n' % (a.help if a.help else '')

    if len(subparsers):
        r += '\n' + heading('COMMANDS', level)
        r += '\n'
        r += '%s\n' % ', '.join(subparsers.keys())
        for name, sub in subparsers.items():
            r += '\n%s\n' % generate_parser(sub, name, level + 1)

    if parser.epilog:
        r += parser.epilog

    if hasattr(parser, 'markdown_epilog'):
        r += parser.markdown_epilog

    return r


def generate_markdown(parser, program_name=None):
    if program_name is None:
        program_name = parser.prog

    return generate_parser(parser, program_name)

