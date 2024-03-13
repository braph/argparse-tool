#!/usr/bin/python3

import sys
from . import shell, utils

class FishCompleter(shell.ShellCompleter):
    # Important: If the completion has '-f', it has to be specified *first*

    def none(self):
        return []

    def choices(self, choices):
        return ['-f', '-a', shell.escape(' '.join(shell.escape(str(c)) for c in choices))]

    def command(self):
        return ['-f', '-a', "'(__fish_complete_command)'"]

    def directory(self, glob_pattern=None):
        if glob_pattern:
            return ['-f', '-a', "(__fish_complete_directories %s)'" % shell.escape(glob_pattern)]
        return ['-f', '-a', "'(__fish_complete_directories)'"]

    def file(self, glob_pattern=None):
        if glob_pattern:
            print("Warning, glob_pattern `%s' ignored\n" % glob_pattern, file=sys.stderr)
        return ['-F']

    def group(self):
        return ['-f', '-a', "'(__fish_complete_groups)'"]

    def hostname(self):
        return ['-f', '-a', "'(__fish_print_hostnames)'"]

    def pid(self):
        return ['-f', '-a', "'(__fish_complete_pids)'"]

    def process(self):
        return ['-f', '-a', "'(__fish_complete_proc)'"]

    def range(self, range):
        if range.step == 1:
            return ['-f', '-a', f"'(seq {range.start} {range.stop})'"]
        else:
            return ['-f', '-a', f"'(seq {range.start} {range.step} {range.stop})'"]

    def service(self):
        return ['-f', '-a', "'(__fish_systemctl_services)'"]

    def user(self):
        return ['-f', '-a', "'(__fish_complete_users)'"]

    def variable(self):
        return ['-f', '-a', "'(set -n)'"]


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
      choices=[],              # Add those words for completion
      flags=set()              # Add those flags (without leading dash)
    ):

    r = ''
    conditions = []
    flags = set(flags)

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

    if 'r' in flags and 'f' in flags: # -r -f is the same as -x
        flags.add('x')

    if 'x' in flags: # -x implies -r -f
        flags.discard('r')
        flags.discard('f')

    if len(flags):
        flags = ' -' + ''.join(flags)
    else:
        flags = ''

    return 'complete -c ' + shell.escape(program_name) + flags + r

def complete_option(action, program_name, parent_commands=[]):
    completer = FishCompleter()
    completion_args = completer.complete(*action.complete)

    flags = set() # Drop '-f' and add it to flags
    if len(completion_args) and completion_args[0] == '-f':
        flags.add('f')
        completion_args.pop(0)

    r = make_complete(
        program_name,
        requires_argument   = action.takes_args,
        description         = action.help,
        seen_words          = parent_commands,
        positional          = None,
        short_options       = action.get_short_options(),
        long_options        = action.get_long_options(),
        conflicting_options = action.get_conflicting_options(),
        flags               = flags
    )

    return (r + ' ' + ' '.join(completion_args)).rstrip()

def complete_positional(action, program_name, parent_commands=[]):
    completer = FishCompleter()
    completion_args = completer.complete(*action.complete)

    flags = set() # Drop '-f' and add it to flags
    if len(completion_args) and completion_args[0] == '-f':
        flags.add('f')
        completion_args.pop(0)

    r = make_complete(
        program_name,
        requires_argument   = action.takes_args,
        description         = action.help,
        seen_words          = parent_commands,
        positional          = action.get_positional_num(),
        flags               = flags
    )

    return (r + ' ' + ' '.join(completion_args)).rstrip()

def complete_subparsers(action, program_name, parent_commands=[]):
    r = ''

    for name, subparser in action.subcommands.items():
        # Here we add the subcommand including its description
        r += f'# command {name}\n'
        r += make_complete(
            program_name,
            no_files       = True,
            description    = subparser.help,
            choices        = [name],
            seen_words     = parent_commands,
            #not_seen_words = sorted(parser.get_subparsers().keys()),
            positional     = action.get_positional_num()
            # we only want to complete a subparsers `name` if it is not yet given on commandline
        ) + '\n'

        # Recursive call to generate completion for a subcommand.
        r += complete_parser(subparser, program_name, parent_commands + [name])

    return r

def complete_parser(parser, program_name, parent_commands=[]):
    # `parent_commands` is used to ensure that options of a command only show up
    #  if the command is present on the commandline. (see `seen_words`)

    r = ''

    for action in parser.get_options():
        r += '%s\n' % complete_option(action, program_name, parent_commands)

    for action in parser.get_positionals():
        r += '%s\n' % complete_positional(action, program_name, parent_commands)

    if parser.get_subparsers_option():
        r += complete_subparsers(parser.get_subparsers_option(), program_name, parent_commands)

    return r

def generate_completion(parser, program_name=None):
    if program_name is None:
        program_name = parser.prog

    return complete_parser(parser, program_name)
