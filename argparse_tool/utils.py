#!/usr/bin/python3

import sys, argparse

# =============================================================================
# Utility functions
# =============================================================================

def type2str(type):
    try:
        return {str:   'str',
                int:   'int',
                bool:  'bool',
                float: 'float'}[type]
    except:
        return '%r' % type

def limit_choices(choices, n=10):
    choices = list(choices)
    if len(choices) > n:
        return choices[:10] + ['...']
    return choices

# =============================================================================
# Functions for enhancing ArgumentParsers information
# =============================================================================

def add_help_to_subparsers(parser):
    ''' Adds `.help` to the subparsers of parser '''
    for a in parser._actions:
        if isinstance(a, argparse._SubParsersAction):
            i = 0
            for name, subparser in a.choices.items():
                add_help_to_subparsers(subparser)
                subparser.help = \
                subparser.description = a._get_subactions()[i].help
                i += 1

def add_parent_parsers(parser, parent=None):
    parser.parent = parent
    for p in parser.get_subparsers().values():
        add_parent_parsers(p, parser)

# =============================================================================
# Functions for getting information about an Action object
# =============================================================================

def action_complete(self, action, *a):
    setattr(self, 'completer', (action, *a))
    return self

def action_requires_args(action):
    if action.nargs: # nargs takes precedence
        return action.nargs == '+' or (action.nargs.isdigit() and int(action.nargs))

    # Check by action
    return isinstance(action, (
        argparse._StoreAction,
        argparse._AppendAction,
        argparse._ExtendAction) )

def action_takes_args(action):
    try:    return action.nargs in '?+*'
    except: return action.nargs != 0
    #return isinstance(action, argparse.BooleanOptionalAction)

def action_get_metavar(action):
    if action.takes_args():
        if action.metavar:
            return action.metavar
        elif action.type is not None:
            return type2str(action.type)
        else:
            return action.dest

    return '' # TODO raise?

def action_get_short_options(action):
    return list(sorted([o for o in action.option_strings if not o.startswith('--')]))

def action_get_long_options(action):
    return list(sorted([o for o in action.option_strings if o.startswith('--')]))

a = argparse.Action
a.complete          = action_complete
a.requires_args     = action_requires_args
a.takes_args        = action_takes_args
a.get_metavar       = action_get_metavar
a.get_short_options = action_get_short_options
a.get_long_options  = action_get_long_options

# =============================================================================
# Functions for getting information about an ArgumentParsers object
# =============================================================================

def parser_get_all_optstrings(parser):
    for a in parser._actions:
        for o in a.option_strings:
            yield o

def parser_get_conflicting_options(parser, action):
    action_conflicts = {}

    for mutex_group in parser._mutually_exclusive_groups:
        group_actions = mutex_group._group_actions
        for i, mutex_action in enumerate(mutex_group._group_actions):
            conflicts = action_conflicts.setdefault(mutex_action, [])
            conflicts.extend(group_actions[:i])
            conflicts.extend(group_actions[i + 1:])

    return action_conflicts.get(action, [])

def parser_get_conflicting_option_strings(parser, action):
    option_strings = set()

    for a in parser.get_conflicting_options(action):
        option_strings.update(a.option_strings)

    return list(option_strings)

def parser_get_help(o):
    try:    return o.help
    except: return o.description

def parser_get_options(parser, only_with_arguments=False):
    result = []
    for a in parser._actions:
        if len(a.option_strings) >= 1 and (only_with_arguments is False or a.takes_args()):
            result.append(a)
    return result

def parser_get_positionals(parser):
    return [a for a in parser._actions if not a.option_strings]

def parser_get_positional_num(parser, action):
    positionals = []

    while parser is not None:
        for a in reversed(parser._actions):
            if not a.option_strings:
                positionals.append(a)

        parser = parser.parent

    positionals = list(reversed(positionals))

    return positionals.index(action) + 1

def parser_get_subparsers(parser):
    for a in parser._actions:
        if isinstance(a, argparse._SubParsersAction):
            return a.choices
    return {}

p = argparse.ArgumentParser
p.get_all_optstrings             = parser_get_all_optstrings
p.get_conflicting_options        = parser_get_conflicting_options
p.get_conflicting_option_strings = parser_get_conflicting_option_strings
p.get_help                       = parser_get_help
p.get_options                    = parser_get_options
p.get_positionals                = parser_get_positionals
p.get_positional_num             = parser_get_positional_num
p.get_subparsers                 = parser_get_subparsers

