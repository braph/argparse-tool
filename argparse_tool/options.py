#!/usr/bin/python3

import sys
from collections import OrderedDict

# TODO: what about empty option strings?

class OptionStrings(list):
    def __init__(self, option_strings):
        if isinstance(option_strings, str):
            super().__init__(option_strings.split('|'))
        else:
            super().__init__(option_strings)

        num_positionals = 0
        num_options = 0
        for option_string in self:
            if option_string.startswith('-'):
                num_options += 1
            else:
                num_positionals += 1

        if num_positionals and num_options:
            raise Exception('Positional arguments and options cannot be mixed')

        if num_positionals > 1:
            raise Exception('Can only store one positional argument')

    def is_positional(self):
        return not self[0].startswith('-')

    def is_option(self):
        return self[0].startswith('-')

class Options:
    def __init__(self, program_name, help=None, parent=None):
        self.prog = program_name
        self.help = help
        self.parent = parent
        self.options = []
        self.positionals = []
        self.subparsers = None

        assert isinstance(self.prog, str)
        assert isinstance(self.help, (str, None.__class__))
        assert isinstance(self.parent, (Options, None.__class__))

    def add(self, option_strings, metavar='', help='', complete=None, takes_args=True):
        option = Option(self, option_strings, metavar=metavar, help=help, complete=complete, takes_args=takes_args)
        self.options.append(option)

    def add_mutually_exclusive_group(self):
        group = MutuallyExclusiveGroup(self)
        return group

    def add_subparsers(self, name='command', help=''):
        self.subparsers = SubparsersOption(self, name, help)
        self.options.append(self.subparsers)
        return self.subparsers

    def get_subparsers(self):
        for option in self.options:
            if option.is_subparser():
                return option.subcommands
        return {}

    def get_subparsers_option(self):
        return self.subparsers

    def get_options(self, only_with_arguments=False):
        result = []
        for o in self.options:
            if o.option_strings.is_option() and (only_with_arguments is False or o.takes_args):
                result.append(o)
        return result

        return self.options

    def get_option_strings(self, only_with_arguments=False):
        option_strings = []
        for o in self.get_options(only_with_arguments=only_with_arguments):
            option_strings.extend(o.option_strings)
        return option_strings

    def get_all_optstrings(self):
        option_strings = []
        for o in self.options:
            if o.is_option():
                option_strings.extend(o.option_strings)
        return option_strings

    def get_positionals(self): # TODO
        return [o for o in self.options if o.is_positional() and not o.is_subparser()]

    def __repr__(self):
        return '{\nprog: %r,\nhelp: %r,\noptions: %r}' % (
            self.prog, self.help, self.options)

class Option:
    def __init__(self, parent, option_strings, metavar='', help='', complete=None, exclusive_group=None, takes_args=True):
        self.parent = parent
        self.option_strings = OptionStrings(option_strings)
        self.metavar = metavar
        self.help = help
        self.group = exclusive_group
        self.takes_args = takes_args
        if complete:
            self.complete = complete
        else:
            self.complete = ('none',)

    def get_options(self):
        return self.option_strings

    def is_option(self):
        return self.option_strings.is_option()

    def is_positional(self):
        return self.option_strings.is_positional()

    def is_subparser(self):
        return False

    def takes_args(self):
        return (self.complete != None)

    def get_short_options(self):
        # TODO?
        return list(sorted([o for o in self.option_strings if not o.startswith('--')]))

    def get_long_options(self):
        return list(sorted([o for o in self.option_strings if o.startswith('--')]))

    def get_conflicting_options(self):
        if not self.group:
            return []
        options = self.group.get_all_options()
        for option in self.option_strings:
            options.remove(option)
        return options

    def get_positional_num(self):
        positionals = []

        parser = self.parent
        while parser is not None:
            all_positionals = parser.get_positionals()
            if parser.get_subparsers_option():
                all_positionals.append(parser.get_subparsers_option())

            for o in reversed(all_positionals):
                positionals.append(o)

            parser = parser.parent

        positionals = list(reversed(positionals))

        return positionals.index(self) + 1

    def __repr__(self):
        return '{option_strings: %r, metavar: %r, help: %r}' % (
            self.option_strings, self.metavar, self.help)

class SubparsersOption(Option):
    def __init__(self, parent, name, help):
        self.parent = parent
        self.subcommands = OrderedDict()
        self.help  = ''
        self.option_strings = OptionStrings([name])
        self.complete = ('choices', [])

    def is_subparser(self):
        return True

    def add_options_object(self, options):
        options.parent = self.parent
        self.subcommands[options.prog] = options
        self.complete[1].append(options.prog)

    def add_options(self, name, help=''):
        options = Options(name, help=help, parent=self.parent)
        self.subcommands[options.prog] = options
        self.complete[1].append(options.prog)
        return options

    def __repr__(self):
        return '{help: %r, subcommands %r}' % (
            self.help, self.subcommands)

class MutuallyExclusiveGroup:
    def __init__(self, parent):
        self.parent = parent
        self.options = []

    def add(self, option_strings, metavar='', help='', complete=None, takes_args=True):
        ''' Creates and adds a new option '''
        option = Option(self.parent, option_strings, exclusive_group=self,
                        metavar=metavar, help=help, complete=complete, takes_args=takes_args)
        self.options.append(option)
        self.parent.options.append(option)

    def add_option(self, option):
        ''' Adds an option object '''
        self.options.append(option)
        option.parent = self.parent
        option.group = self

    def get_all_options(self):
        r = []
        for option in self.options:
            for option_string in option.option_strings:
                r.append(option_string)
        return r
        
import argparse

def Action_Get_Metavar(action):
    if action.metavar:
        return action.metavar
    elif action.type is int:
        return 'INT'
    elif action.type is bool:
        return 'BOOL'
    elif action.type is float:
        return 'FLOAT'
    else:
        return action.dest.upper()

def ArgumentParser_to_Options(parser, prog=None, description=None):

    def get_option_strings(action):
        # parser.add_argument('foo') results in empty option_strings
        if len(action.option_strings) >= 1:
            return action.option_strings
        else:
            return [action.dest]

    if not description:
        description = parser.description

    if not prog:
        prog = parser.prog

    options = Options(prog, description)

    for action in parser._actions:
        if isinstance(action, argparse._HelpAction):
            options.add('--help|-h', help=action.help, takes_args=False)
        elif isinstance(action, argparse._VersionAction):
            options.add('--version', help=action.help, takes_args=False)
        elif isinstance(action, argparse._StoreTrueAction) or \
             isinstance(action, argparse._StoreFalseAction) or \
             isinstance(action, argparse._StoreConstAction) or \
             isinstance(action, argparse._AppendConstAction) or \
             isinstance(action, argparse._CountAction):

            if hasattr(action, 'completion'):
                raise Exception('Action has completion but takes not arguments', action)

            options.add(
                get_option_strings(action),
                metavar='',
                complete=None,
                help=action.help,
                takes_args=False
            )

        elif isinstance(action, argparse._StoreAction) or \
             isinstance(action, argparse._ExtendAction)or \
             isinstance(action, argparse._AppendAction):

            if action.choices and hasattr(action, 'completion'):
                raise Exception('Action has both choices and completion set', action)

            if action.choices:
                if isinstance(action.choices, range):
                    complete = ('range', action.choices)
                else:
                    complete = ('choices', action.choices)
            elif hasattr(action, 'completion'):
                complete = action.completion
            else:
                complete = None

            options.add(
                get_option_strings(action),
                metavar=Action_Get_Metavar(action),
                complete=complete,
                help=action.help,
                takes_args=True
            )

        elif isinstance(action, argparse.BooleanOptionalAction):
            raise Exception("not supported")

        elif isinstance(action, argparse._SubParsersAction):
            subparsers = OrderedDict()

            for name, subparser in action.choices.items():
                subparsers[name] = {'parser': subparser}

            for action in action._get_subactions():
                subparsers[action.dest]['help'] = action.help

            subp = options.add_subparsers(name='command', help='Subcommands')

            for name, data in subparsers.items():
                suboptions = ArgumentParser_to_Options(data['parser'], name, data['help'])
                subp.add_options_object(suboptions)

        else:
            print('Unknown action type:', type(action), file=sys.stderr)
            raise

    for group in parser._mutually_exclusive_groups:
        exclusive_group = MutuallyExclusiveGroup(options)
        for action in group._group_actions:
            for option in options.get_options():
                for option_string in action.option_strings:
                    if option_string in option.option_strings:
                        exclusive_group.add_option(option)
                        break

    return options

