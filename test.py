#!/usr/bin/python3

import sys
from argparse_tool import options, utils, zsh, bash, fish, printf, man, markdown
#
#o = options.Options('argparse-tool-test', 'Test argument parser for shell completion')
#o.add('--version',    help='Show program version')
#o.add('--file',       help='Complete a file',       complete=('file',))
#o.add('--directory',  help='Complete a directory',  complete=('directory',))
#o.add('--user',       help='Complete a user',       complete=('user',))
#o.add('--group',      help='Complete a group',      complete=('group',))
#o.add('--command',    help='Complete a command',    complete=('command',))
#o.add('--process',    help='Complete a process',    complete=('process',))
#o.add('--pid',        help='Complete a pid',        complete=('pid',))
#o.add('--signal',     help='Complete a signal',     complete=('signal',))
#o.add('--hostname',   help='Complete a hostname',   complete=('hostname',))
#o.add('--variable',   help='Complete a variable',   complete=('variable',))
#o.add('--service',    help='Complete a service',    complete=('service',))
#o.add('--choices',    help='Complete from choices', complete=('choices', (1,'two and a half',3)))
#o.add('--range',      help='Complete a range',      complete=('choices', range(1,9,2)))
#o.add('-f', '--flag', help='A option flag')
#o.add('--integer',    help='Option with integer')
#o.add('-a', '-A', '--argument')
#o.add('--single-quote-in-description',  help="Here is a single quote: '")
#o.add('--double-quote-in-description',  help='Here is a double quote: "')
#o.add('--special-chars-in-description', help='Here are some special chars: $(echo \'\\"`ls`")')
#
#group = o.add_mutually_exclusive_group()
#group.add('--exclusive-1', help='Exclusive 1')
#group.add('--exclusive-2', help='Exclusive 2')
#
#subp = o.add_subparsers(help='commands')
#
#cmdp = subp.add_options('dummy', help='Dummy command')
#
#cmdp = subp.add_options('positionals',  help='For testing positionals')
#cmdp.add('pos', help='First positional',    complete=('choices', ('first1', 'first2', 'first3')))
#cmdp.add('opt', help='Optional positional', complete=('choices', ('optional1', 'optional2') ))
#
#cmdp = subp.add_options('zsh', help='For testing zsh:')
#cmdp.add('--argument-with-colon-in-description', help='Colon follows:')
#
#r = zsh.generate_completion(o)
#print(r)
#raise


import argparse

try:    from argparse_tool import utils
except: argparse.Action.complete = lambda s, *_: s

argp = argparse.ArgumentParser(prog='argparse-tool-test',
    description='Test argument parser for shell completion')

argp.add_argument('--version',        action='version')
argp.add_argument('--file',           help='Complete a file').complete('file')
argp.add_argument('--directory',      help='Complete a directory').complete('directory')
argp.add_argument('--user',           help='Complete a user').complete('user')
argp.add_argument('--group',          help='Complete a group').complete('group')
argp.add_argument('--command',        help='Complete a command').complete('command')
argp.add_argument('--process',        help='Complete a process').complete('process')
argp.add_argument('--pid',            help='Complete a pid').complete('pid')
argp.add_argument('--signal',         help='Complete a signal').complete('signal')
argp.add_argument('--hostname',       help='Complete a hostname').complete('hostname')
argp.add_argument('--variable',       help='Complete a variable').complete('variable')
argp.add_argument('--service',        help='Complete a service').complete('service')
argp.add_argument('--choices', '-c',  help='Complete from choices', choices=(1,'two and a half',3))
argp.add_argument('-f', '--flag',     help='A option flag', action='store_true')
argp.add_argument('--range',          help='Complete a range', type=int, choices=range(1,9,2))
#
argp.add_argument('--store-true',     help='A option flag', action='store_true')
argp.add_argument('--store-false',    help='A option flag', action='store_false')
argp.add_argument('--store-const',    help='A option flag', action='store_const', const='bar')
argp.add_argument('--append-const',   help='A option flag', action='append_const', const='bar')
argp.add_argument('--append',         help='A option flag', action='append')
argp.add_argument('--count',          help='A option flag', action='count')
argp.add_argument('--extend',         help='A option flag', action='extend')
#
argp.add_argument('--integer',    help='Option with integer', type=int)
argp.add_argument('-a', '-A', '--argument') # TODO
argp.add_argument('--single-quote-in-description',  help="Here is a single quote: '")
argp.add_argument('--double-quote-in-description',  help='Here is a double quote: "')
argp.add_argument('--special-chars-in-description', help='Here are some special chars: $(echo \'\\"`ls`")')
group = argp.add_mutually_exclusive_group()
group.add_argument('--exclusive-1', action='store_true')
group.add_argument('--exclusive-2', action='store_true')

subp = argp.add_subparsers(description='commands')

cmdp = subp.add_parser('dummy', help='Dummy command')

cmdp = subp.add_parser('positionals',  help='For testing positionals')
cmdp.add_argument('pos', help='First positional', choices=('first1', 'first2', 'first3'))
cmdp.add_argument('opt', help='Optional positional', choices=('optional1', 'optional2'), nargs='?')

cmdp = subp.add_parser('zsh', help='For testing zsh:')
cmdp.add_argument('--argument-with-colon-in-description', help='Colon follows:')


o = options.ArgumentParser_to_Options(argp)
#print(repr(o))

print('bash', file=sys.stderr)
bash = bash.generate_completion(o)

print('zsh', file=sys.stderr)
zsh = zsh.generate_completion(o)

print('fish', file=sys.stderr)
fish = fish.generate_completion(o)

print(bash)
