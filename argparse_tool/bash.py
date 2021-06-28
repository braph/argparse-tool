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


_bash_complete = BashCompleter().complete

def _bash_complete_action(action, append=True):
    r = _bash_complete(*shell.action_get_completer(action))
    return r.to_shell(append)

def _bash_case_option_strings(action):
    return '|'.join(map(shell.escape, sorted(action.option_strings)))

def _bash_make_optstring_test_pattern(option_strings):
    # Return the smallest pattern for matching optionals which take arguments
    # [[ $string == $pattern ]]

    option_strings = sorted(option_strings)

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
        return '-@([%s])' % ''.join(sorted(long_opts))

    return "-@([%s]|-@(%s))" % (''.join(sorted(short_opts)), '|'.join(sorted(long_opts)))

def _bash_complete_parser(info, parser, funcname, parent_parsers=[]):
    # The completion function returns 0 (success) if there was a match.

    funcname    = shell.make_identifier(funcname)
    options     = parser.get_options()
    positionals = parser.get_positionals()
    subparsers  = parser.get_subparsers()

    r  = f'{funcname}() {{\n'

    if len(parent_parsers) == 0:
        # The root parser makes those variables local and sets up the completion.
        # Calls to subparser function modify these variables.
        r += '  local cur prev words cword split args w\n'
        r += '  _init_completion -s || return\n'
        r += '\n'

        if len(positionals):
            # The call to _count_args allows us to complete positionals later.
            option_strings = []
            for a in filter(lambda a: a.takes_args(), parser._actions):
                option_strings.extend(a.option_strings)
            exclude_pattern = _bash_make_optstring_test_pattern(option_strings)
            r += '  _count_args "" "%s"\n' % exclude_pattern

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
        for a in options:
            if a.takes_args():
                s += '    %s)\n' % _bash_case_option_strings(a)
                s += '       %s\n'  % _bash_complete_action(a, False)
                s += '       return 0;;\n'
        if s:
            r += '  case "$prev" in\n'
            r += s
            r += '  esac\n'
            r += '\n'

    r += '  [[ "$cur" = -* ]] && %s\n' % _bash_complete('choices', parser.get_all_optstrings()).to_shell(True)
    r += '\n'

    if len(positionals):
        r += '  case $args in\n'
        for a in positionals:
            r += '    %d)\n' % (info.get_positional_index(a) + 1)
            r += '       %s\n' % _bash_complete_action(a)
            r += '       return 0;;\n'
        r += '  esac\n'
        r += '\n'

    r += '  return 1\n'
    r += '}\n\n'

    for name, sub in subparsers.items():
        f = shell.make_identifier('_%s_%s' % (parser.prog, name))
        r += _bash_complete_parser(info, sub, f, parent_parsers + [parser])

    return r

def generate_completion(parser, prog=None):
    if prog is None:
        prog = parser.prog

    info = utils.ArgparseInfo.create(parser)
    funcname = shell.make_identifier('_'+prog)
    r  = '#!/bin/bash\n\n'
    r += _bash_complete_parser(info, parser, funcname).rstrip()
    r += '\n\n'
    r += 'complete -F %s %s' % (funcname, prog)
    return r
