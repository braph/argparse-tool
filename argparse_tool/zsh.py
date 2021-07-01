#!/usr/bin/python3

import argparse, sys
from . import shell, utils

class ZshCompleter(shell.ShellCompleter):
    def none(self):
        return "'()'"

    def choices(self, choices):
        if hasattr(choices, 'items'):
            return shell.escape('((%s))' % ' '.join(
                shell.escape('%s\\:%s' % (str(val), desc)) for val, desc in choices.items()
            ))
        else:
            return shell.escape("(%s)" % (' '.join(shell.escape(str(c)) for c in choices)))

    def command(self):
        return '_command_names'

    def directory(self, glob_pattern=None):
        if not glob_pattern:
            return '_directories'
        else:
            return shell.escape('_directories -G '+glob_pattern)

    def file(self, glob_pattern=None):
        if not glob_pattern:
            return '_files'
        else:
            return shell.escape('_files -G '+glob_pattern)

    def group(self):
        return '_groups'

    def hostname(self):
        return '_hosts'

    def pid(self):
        return '_pids'

    def process(self):
        return '_process_names'

    def range(self, range):
        if range.step == 1:
            return f"'({{{range.start}..{range.stop}}})'"
        else:
            return f"'({{{range.start}..{range.stop}..{range.step}}})'"

    def user(self):
        return '_users'

    def variable(self):
        return '_vars'


complete = ZshCompleter().complete

def escape_colon(s):
    return s.replace(':', '\\:')

def make_argument_option_spec(
        option_strings,
        conflicting_arguments=[],
        description = '',
        takes_args=False,
        metavar = '',
        action = ''
    ):
    # '(--option -o)'{--option=,-o+}'[Option description]':Metavar:'action'

    # Any literal colon in an optname, message, or action must be preceded by a backslash, `\:'.
    conflicting_arguments = [escape_colon(s) for s in sorted(conflicting_arguments)]
    option_strings        = [escape_colon(s) for s in sorted(option_strings)]
    description           = escape_colon('['+description+']') if description else ''
    metavar               = escape_colon(metavar)

    if conflicting_arguments:
        conflicting_arguments = shell.escape("(%s)" % ' '.join(escape_colon(s) for s in conflicting_arguments))

    if takes_args:
        option_strings = [o+'+' if len(o) == 2 else o+'=' for o in option_strings]

    if len(option_strings) == 1:
        option_strings = option_strings[0]
    else:
        option_strings = '{%s}' % ','.join(option_strings)

    #conflicting_arguments = shell.escape(conflicting_arguments)
    description = shell.escape(description, escape_empty_string=False)
    metavar = shell.escape(metavar, escape_empty_string=False)

    return f'{conflicting_arguments}{option_strings}{description}:{metavar}:{action}'

def complete_action(parser, action):
    if action.option_strings:
        return make_argument_option_spec(
            action.option_strings,
            conflicting_arguments = parser.get_conflicting_option_strings(action),
            description = action.help,
            takes_args = action.takes_args(),
            metavar = action.get_metavar(),
            action = complete(*shell.action_get_completer(action)))

    elif isinstance(action, argparse._SubParsersAction):
        choices = {}
        for name, subparser in parser.get_subparsers().items():
            choices[name] = subparser.get_help()
        return ":command:" + complete('choices', choices)
        #return "':command:%s'" % shell.make_subparser_identifier(parser.prog)
    else:
        return ":%s:%s" % (
            shell.escape(escape_colon(action.help)) if action.help else '',
            complete(*shell.action_get_completer(action)))

def generate_completion_function(parser, funcname):
    args = []
    trailing_functions = ''
    r =  f'{funcname}() {{\n'

    for action in parser._actions:
        args.append(complete_action(parser, action))

    if len(parser.get_subparsers()):
        args.append("'*::arg:->args'")

    if len(args):
        r += '  _arguments \\\n    %s\n' % '\\\n    '.join(args)

    subparsers = parser.get_subparsers()
    if len(subparsers):
        r += '  for w in $line; do\n'
        r += '    case $w in\n'
        for name, subparser in subparsers.items():
            sub_funcname = shell.make_identifier(f'_{funcname}_{name}')
            trailing_functions += generate_completion_function(subparser, sub_funcname)
            r += f'      ({name}) {sub_funcname}; break;;\n'
        r += '    esac\n'
        r += '  done\n'
    r += '}\n\n'

    return r + trailing_functions

def generate_completion(parser, program_name=None):
    if program_name is None:
        program_name = parser.prog

    completion_funcname = '_' + shell.make_identifier(program_name)
    completion_functions = generate_completion_function(parser, completion_funcname)

    return f'''\
#compdef {program_name}

{completion_functions.rstrip()}

{completion_funcname} "$@"
'''

