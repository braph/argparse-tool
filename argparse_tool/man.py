#!/usr/bin/python3

from collections import OrderedDict
import datetime, sys, argparse
from . import utils, shell

# preferred order, taken from man-pages(7)
_ordered_sections = OrderedDict([
    ('NAME',           None),
    ('SYNOPSIS',       None),
    ('CONFIGURATION',  None),
    ('DESCRIPTION',    None),
    ('OPTIONS',        None),
    ('COMMANDS',       None), # added
    ('EXIT STATUS',    None),
    ('RETURN VALUE',   None),
    ('ERRORS',         None),
    ('ENVIRONMENT',    None),
    ('FILES',          None),
    ('VERSIONS',       None),
    ('CONFORMING TO',  None),
    ('NOTES',          None),
    ('BUGS',           None),
    ('EXAMPLE',        None),
    ('SEE ALSO',       None),
])

class ManWriter():
    def __init__(self):
        self.s = ''

    def ensure_nl(self):
        if len(self.s):
            self.s = self.s.rstrip()
            self.s += '\n'
        return self

    def title(self, title, section, date, source, manual):
        self.ensure_nl()
        self.s += '.TH %s %s %s %s %s\n' % (
            title.upper(), section, date, source, manual)
        return self

    def section(self, name):
        self.ensure_nl()
        self.s += '.SH %s\n' % (name,)
        return self

    def bold(self, text):
        self.ensure_nl()
        self.s += '.B %s' % (text,)
        return self

    def italic(self, text):
        self.ensure_nl()
        self.s += '.I %s' % (text,)
        return self

    def bold_roman(self, text):
        self.ensure_nl()
        self.s += '.BR %s' % (text,)
        return self

    def indented_paragraph(self, text):
        self.ensure_nl()
        self.s += '.IP "%s"\n' % (text,)
        return self

    def append(self, s):
        self.s += str(s)
        return self

    def see_also(self, pages):
        for p in pages:
            self.bold_roman(p)
        return self


    def __str__(self):
        return self.s

class ManPage():
    def __init__(self):
        self.section  = 1
        self.name     = None
        self.package  = None
        self.date     = str(datetime.date.today())
        #self.see_also = None
        self.sections = _ordered_sections.copy()

    def write(self):
        writer = ManWriter()
        writer.title(
            self.name.upper(), self.section, self.date,
            self.package,
            self.name.upper()
        )

        for name, text in self.sections.items():
            if callable(text):
                text = text()

            if text is None:
                continue

            writer.section(name)
            if isinstance(text, dict):
                NamedList(text).write(writer)
            elif isinstance(text, list):
                SeeAlso(text).write(writer)
            else:
                writer.append(text)

        return writer.s

class NamedList:
    def __init__(self, list):
        self.list = list

    def write(self, writer):
        for title, text in self.list.items():
            writer.indented_paragraph(title)
            writer.append(text)

class SeeAlso:
    def __init__(self, pages):
        self.pages = pages

    def write(self, writer):
        pages = [(p.replace(')', '')+'(1').split('(') for p in self.pages]
        pages = sorted(pages, key=lambda p: p[0])
        for p in pages:
            writer.bold_roman("%s (%s)" % (p[0].strip(), p[1].strip()))

# TODO: .SS subsection on mutex/option groups
class ManPageArgparse(ManPage):
    def __init__(self, parser, prog=None):
        super().__init__()
        if not prog:
            prog = parser.prog
        self.parser  = parser
        self.prog    = prog
        self.name    = prog
        self.package = prog
        self.sections['NAME']        = self._name
        self.sections['SYNOPSIS']    = self.synopsis
        self.sections['DESCRIPTION'] = self.description
        self.sections['OPTIONS']     = self.options
        self.sections['COMMANDS']    = self.commands
        self.sections['AUTHOR']      = self.author
        self.sections['COPYRIGHT']   = None

    def _name(self):
        return '%s - %s\n' % (self.prog, parser.get_help())

    def synopsis(self):
        writer = ManWriter()
        writer.bold(self.prog).italic('[OPTIONS]')
        for a in self.parser._actions:
            if isinstance(a, argparse._SubParsersAction):
                writer.bold('command') # TODO
        return writer.s

    def description(self):
        return ManWriter().append(parser.get_help()).s

    def options(self):
        writer = ManWriter()
        for a in self.parser._actions:
            self.option(writer, a)
        return writer.s

    def option(self, writer, action):
        if not action.option_strings:
            return

        writer.indented_paragraph(', '.join(action.option_strings))
        if action.choices:
            writer.append('[%s]' % ', '.join(map(str, utils.limit_choices(action.choices))))
        elif action.metavar:
            writer.append(' ' + action.metavar)
        elif shell.action_takes_args(action) and action.type is not None and action.type is not str:
            writer.append(utils.type2str(typ))

        writer.append('\n     %s\n' % action.help)


    def commands(self):
        writer = ManWriter()
        subparsers = self.parser.get_subparsers()
        if len(subparsers):
            writer.append('%s\n' % ', '.join(subparsers.keys()))
            for name, sub in subparsers.items():
               #sub.parser.prog = name
               pass # TODO
        return writer.s

    def author(self):
        return None


def generate_man(p, prog=None):
    if prog is None:
        prog = p.prog

    if hasattr(p.parser, 'man_page'):
        manpage = p.man_page
    else:
        raise
        manpage = ManPageArgparse(p, prog)

    return manpage.write()

