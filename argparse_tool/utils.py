#!/usr/bin/python3

import sys, argparse

def action_complete(self, action, *a):
    setattr(self, 'completer', (action, *a))
    return self

argparse.Action.complete = action_complete

def get_all_optstrings(parser):
    for a in parser._actions:
        for o in a.option_strings:
            yield o

argparse.ArgumentParser.get_all_optstrings = get_all_optstrings

def get_subparsers(parser):
    for a in parser._actions:
        if isinstance(a, argparse._SubParsersAction):
            return a.choices
    return {}

argparse.ArgumentParser.get_subparsers = get_subparsers

def get_help(o):
    try:    return o.help
    except: return o.description

argparse.ArgumentParser.get_help = get_help

def action_takes_args(action):
    try:    return action.nargs in '?+*'
    except: return action.nargs != 0
    #return isinstance(action, argparse.BooleanOptionalAction)

argparse.Action.takes_args = action_takes_args

def action_requires_args(action):
    if action.nargs: # nargs takes precedence
        return action.nargs == '+' or (action.nargs.isdigit() and int(action.nargs))

    # Check by action
    return isinstance(action, (
        argparse._StoreAction,
        argparse._AppendAction,
        argparse._ExtendAction) )

argparse.Action.requires_args = action_requires_args

def action_get_short_long_options(action):
    r = ([], [])
    for s in action.option_strings:
        r[int(s.startswith('--'))].append(s)
    return r

argparse.Action.get_short_long_options = action_get_short_long_options

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

def parser_get_options(parser):
    return [a for a in parser._actions if a.option_strings]

argparse.ArgumentParser.get_options = parser_get_options

def parser_get_positionals(parser):
    return [a for a in parser._actions if not a.option_strings]

argparse.ArgumentParser.get_positionals = parser_get_positionals

class ArgparseInfo:
    def __init__(self):
        self.action_conflicts = {}
        self.positionals = {}

    def yield_all_option_strings(self):
        for a in self.actions:
            for o in a.option_strings:
                yield o

    def get_conflicting_options(self, action):
        return self.action_conflicts.get(action, [])

    def get_positional_index(self, action):
        return self.positionals[action]

    @staticmethod
    def create(parser):
        info = ArgparseInfo()
        ArgparseInfoBuilder(info, parser)
        return info

class ArgparseInfoBuilder:
    def __init__(self, info, parser, parent=None):
        self.parser = parser
        self.info = info
        self.parent = parent
        self.postional_count = parent.postional_count if parent else 0

        for a in parser._actions:
            self.handle_action(a)
            if isinstance(a, argparse._SubParsersAction):
                i = 0
                for name, subparser in a.choices.items():
                    sub = ArgparseInfoBuilder(info, subparser, self)
                    sub.parser.help = a._get_subactions()[i].help
                    i += 1

    def handle_action(self, action):
        if not action.option_strings:
            self.info.positionals[action] = self.postional_count
            self.postional_count += 1
            return

        for mutex_group in self.parser._mutually_exclusive_groups:
            group_actions = mutex_group._group_actions
            for i, mutex_action in enumerate(mutex_group._group_actions):
                conflicts = self.info.action_conflicts.setdefault(mutex_action, [])
                conflicts.extend(group_actions[:i])
                conflicts.extend(group_actions[i + 1:])

def type2str(type):
    try:
        return {
            str:    'str',
            int:    'int',
            bool:   'bool',
            float:  'float'
        }[type]
    except:
        return '%r' % type

def limit_choices(choices, n=10):
    choices = list(choices)
    if len(choices) > n:
        return choices[:10] + ['...']
    return choices
