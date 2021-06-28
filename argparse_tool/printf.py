#!/usr/bin/python3

import re

def make_identifier(s):
    ''' Make `s` a valid C identifier '''
    s = s.replace('-', '_')
    s = re.sub('[^a-zA-Z0-9_]', '', s)
    while '__' in s:
        s = s.replace('__', '_')
    return s.lstrip('0123456789')

def str_to_c(s):
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = '"' + s.replace('\n', '\\n"\n"') + '"'
    return s

def define_macro(name, value):
    return '#define %s %s' % (name, value.replace('\n', '\\\n '))

def create_macro_name(parser_names):
    return make_identifier('%s_HELP_TEXT' % '_'.join(parser_names)).upper()

def generate_printf_usage(p, prog='%s', macro=create_macro_name, parsers=[]):
    if prog is None:
        prog = p.prog

    parsers = parsers.copy()
    parsers.append(p.prog)

    r = ''

    macro_name = macro(parsers)

    p.prog, prog_old = '$$$ PROG $$$', p.prog
    help = p.format_help()
    p.prog = prog_old

    help = str_to_c(help)
    help = help.replace('%', '%%')
    help = help.replace('$$$ PROG $$$', prog)
    r += '%s\n' % define_macro(macro_name, help)

    for name, sub in p.get_subparsers().items():
        sub.prog = name
        r += '%s\n' % generate_printf_usage(sub, prog, macro, parsers)

    return r

