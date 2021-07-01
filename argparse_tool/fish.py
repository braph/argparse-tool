#!/usr/bin/python3

import sys
from . import shell, utils

class FishCompleter(shell.ShellCompleter):
    def none(self):
        return ''

    def choices(self, choices):
        return '-f -a ' + shell.escape(' '.join(shell.escape(str(c)) for c in choices))

    def command(self):
        return "-f -a '(__fish_complete_command)'"

    def directory(self, glob_pattern=None):
        if glob_pattern:
            return "-f -a '(__fish_complete_directories %s)'" % shell.escape(glob_pattern)
        return "-f -a '(__fish_complete_directories)'"

    def file(self, glob_pattern=None):
        if glob_pattern:
            print("Warning, glob_pattern `%s' ignored\n" % glob_pattern, file=sys.stderr)
        return '-F'

    def group(self):
        return "-f -a '(__fish_complete_groups)'"

    def hostname(self):
        return "-f -a '(__fish_print_hostnames)'"

    def pid(self):
        return "-f -a '(__fish_complete_pids)'"

    def process(self):
        return "-f -a '(__fish_complete_proc)'"

    def range(self, range):
        if range.step == 1:
            return f"-f -a '(seq {range.start} {range.stop})'"
        else:
            return f"-f -a '(seq {range.start} {range.step} {range.stop})'"

    def service(self):
        return "-f -a '(__fish_systemctl_services)'"

    def user(self):
        return "-f -a '(__fish_complete_users)'"

    def variable(self):
        return "-f -a '(set -n)'"


_fish_complete = FishCompleter().complete

def join_escaped(l, delimiter=' '):
    return delimiter.join(shell.escape(word) for word in l)

# =============================================================================
# Helper function for creating a `complete` command in fish
# =============================================================================

def make_complete(
      program_name,            # Name of program beeing completed
      short_options=[],        # List of short options
      long_options=[],         # List of long options
      seen_words=[],           # Only show if these words are given on commandline
      not_seen_words=[],       # Only show if these words are not given on commandline
      conflicting_options=[],  # Only show if these options are not given on commandline
      description=None,        # Description
      positional=None,         # Only show if current word number is `positional`
      requires_argument=False, # Option requires an argument
      no_files=False,          # Don't use file completion
      choices=[]               # Add those words for completion
    ):

    r = ''
    flags = set()
    conditions = []

    if no_files:           flags.add('f')
    if requires_argument:  flags.add('r')

    if len(seen_words):
        conditions += ["__fish_seen_subcommand_from %s" % join_escaped(sorted(seen_words))]

    if len(not_seen_words):
        conditions += ["not __fish_seen_subcommand_from %s" % join_escaped(sorted(not_seen_words))]

    if len(conflicting_options):
        conditions += ["not __fish_contains_opt %s" % ' '.join(o.lstrip('-') for o in sorted(conflicting_options))]

    if positional is not None:
        conditions += ["test (__fish_number_of_cmd_args_wo_opts) = %d" % positional]

    if len(conditions):
        r += " -n %s" % shell.escape(' && '.join(conditions))

    for o in sorted(short_options): r += ' -s ' + shell.escape(o.lstrip('-'))
    for o in sorted(long_options):  r += ' -l ' + shell.escape(o.lstrip('-'))
    if description:                 r += ' -d ' + shell.escape(description)

    for s in choices:
        r += ' -a ' + shell.escape(s)

    if 'r' in flags and 'f' in flags:
        flags.remove('r')
        flags.remove('f')
        flags.add('x')

    if len(flags):
        flags = ' -' + ''.join(flags)
    else:
        flags = ''

    return 'complete -c ' + shell.escape(program_name) + flags + r

def complete_action(parser, action, program_name, parent_commands=[]):
    positional = None

    if not action.option_strings:
        positional = parser.get_positional_num(action)

    r = make_complete(
        program_name,
        requires_argument   = action.requires_args(),
        description         = action.help,
        seen_words          = parent_commands,
        positional          = positional,
        short_options       = action.get_short_options(),
        long_options        = action.get_long_options(),
        conflicting_options = parser.get_conflicting_option_strings(action)
    )

    r += ' ' + _fish_complete(*shell.action_get_completer(action))
    return r.rstrip()

def complete_parser(parser, program_name, parent_commands=[]):
    # `parent_commands` is used to ensure that options of a command only show up
    #  if the command is present on the commandline. (see `seen_words`)

    r = ''

    # First, we complete all actions for the current parser.
    for action in parser._actions:
        r += '%s\n' % complete_action(parser, action, program_name, parent_commands)

    for name, subparser in parser.get_subparsers().items():
        # Here we add the subcommand including its description
        r += f'# command {name}\n'
        r += make_complete(
            program_name,
            no_files       = True,
            description    = subparser.get_help(),
            choices        = [name],
            seen_words     = parent_commands,
            not_seen_words = sorted(parser.get_subparsers().keys())
            # we only want to complete a subparsers `name` if it is not yet given on commandline
        ) + '\n'

        # Recursive call to generate completion for a subcommand.
        r += complete_parser(subparser, program_name, parent_commands + [name])

    return r

def generate_completion(parser, program_name=None):
    if program_name is None:
        program_name = parser.prog

    return complete_parser(parser, program_name)
