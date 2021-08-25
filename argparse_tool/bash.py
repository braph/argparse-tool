#!/usr/bin/python3

from . import shell, utils

# $split && return
#_filedir '@(?(d)patch|dif?(f))'
#compgen -F

class BashCompletionCommand:
    ''' Used for completion functions that internally modify COMPREPLY '''
    def __init__(self, cmd):
        self.cmd = cmd

    def to_shell(self, append=False):
        return self.cmd

class BashCompletion:
    def __init__(self, values):
        self.values = values

    def to_shell(self, append=False):
        return 'COMPREPLY%s=(%s)' % (('+' if append else ''), self.values)


def compgen(args, word='"$cur"'):
    return BashCompletion('$(compgen %s -- %s)' % (args, word))

def compreply(values):
    return BashCompletion(values)

class BashCompleter(shell.ShellCompleter):
    def none(self):
        return BashCompletionCommand('')

    def choices(self, choices):
        return compgen('-W '+ shell.escape(' '.join(shell.escape(str(c)) for c in choices)))

    def command(self):
        return compgen('-A command')

    def directory(self, glob_pattern=None):
        if not glob_pattern:
            return compgen('-d')
        else:
            return compgen('-G ' + shell.escape(glob_pattern))

    def file(self, glob_pattern=None):
        if not glob_pattern:
            return compgen('-f')
        else:
            return compgen('-G ' + shell.escape(glob_pattern))

    def group(self):
        return compgen('-A group')

    def hostname(self):
        return compgen('-A hostname')

    def pid(self):
        return BashCompletionCommand('_pids')

    def process(self):
        return BashCompletionCommand('_pnames')

    def range(self, range):
        if range.step == 1:
            return compgen(f"-W '{{{range.start}..{range.stop}}}'")
        else:
            return compgen(f"-W '{{{range.start}..{range.stop}..{range.step}}}'")

    def service(self):
        return compgen('-A service')

    def user(self):
        return compgen('-A user')

    def variable(self):
        return compgen('-A variable')


complete = BashCompleter().complete

def complete_action(action, append=True):
    r = complete(*shell.action_get_completion(action))
    return r.to_shell(append)

def make_switch_case_pattern(strings):
    return '|'.join(map(shell.escape, sorted(strings)))

def make_optstring_test_pattern(option_strings):
    # Return the smallest pattern for matching option_strings [[ $string == $pattern ]]

    option_strings = list(sorted(option_strings))

    if len(option_strings) == 0:
        return '' # TODO?

    if len(option_strings) == 1:
        return option_strings[0]

    if len(option_strings) <= 3:
        return '@(%s)' % '|'.join(option_strings)

    short_opts, long_opts = [], []
    for o in option_strings:
        if   o.startswith('--'):  long_opts.append(o[2:])
        elif o.startswith('-'):   short_opts.append(o[1:])

    if not len(short_opts):
        return '--@(%s)' % '|'.join(sorted(long_opts))

    if not len(long_opts):
        return '-@([%s])' % ''.join(sorted(short_opts))

    return "-@([%s]|-@(%s))" % (''.join(sorted(short_opts)), '|'.join(sorted(long_opts)))

def complete_parser(parser, funcname):
    # The completion function returns 0 (success) if there was a completion match.
    # This return code is used when dealing with subparsers.

    funcname    = shell.make_identifier(funcname)
    options     = parser.get_options()
    positionals = parser.get_positionals()
    subparsers  = parser.get_subparsers()

    r  = f'{funcname}() {{\n'

    if parser.parent is None:
        # The root parser makes those variables local and sets up the completion.
        # Calls to subparser functions modify these variables.
        r += '  local cur prev words cword split args w\n'
        r += '  _init_completion -s || return\n'
        r += '\n'

        if len(positionals):
            # The call to _count_args allows us to complete positionals later using $args.
            option_strings = parser.get_option_strings(only_with_arguments=True)
            r += '  _count_args "" "%s"\n' % make_optstring_test_pattern(option_strings)

    if len(subparsers):
        r += '  for w in "${COMP_WORDS[@]}"; do\n'
        r += '    case "$w" in\n'
        for name in subparsers.keys():
            f = shell.make_identifier('_%s_%s' % (parser.prog, name))
            r += '      %s) %s && return 0;;\n' % (shell.escape(name), f)
        r += '    esac\n'
        r += '  done\n'
        r += '\n'

    if len(options):
        s = ''
        for action in parser.get_options(only_with_arguments=True):
            s += '    %s)\n' % make_switch_case_pattern(action.option_strings)
            code = complete_action(action, False)
            if code:
                s += '       %s\n' % code
            s += '       return 0;;\n'

        if s:
            r += '  case "$prev" in\n'
            r += s
            r += '  esac\n'
            r += '\n'

    r += '  [[ "$cur" = -* ]] && %s\n' % complete('choices', parser.get_all_optstrings()).to_shell(True)
    r += '\n'

    if len(positionals):
        r += '  case $args in\n' # $args is the number of args
        for action in positionals:
            r += '    %d) %s\n' % (parser.get_positional_num(action), complete_action(action))
            r += '       return 0;;\n'
        r += '  esac\n'
        r += '\n'

    r += '  return 1\n'
    r += '}\n\n'

    for name, sub in subparsers.items():
        f = shell.make_identifier('_%s_%s' % (parser.prog, name))
        r += complete_parser(sub, f)

    return r

def generate_completion(parser, program_name=None):
    if program_name is None:
        program_name = parser.prog

    funcname = shell.make_identifier('_'+program_name)
    r  = '#!/bin/bash\n\n'
    r += complete_parser(parser, funcname).rstrip()
    r += '\n\n'
    r += 'complete -F %s %s' % (funcname, program_name)
    return r
