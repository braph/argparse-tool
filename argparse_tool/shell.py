#!/usr/bin/python3

import sys, re, argparse, collections

def make_identifier(s):
    ''' Make `s` a valid shell identifier '''
    s = s.replace('-', '_')
    s = re.sub('[^a-zA-Z0-9_]', '', s)
    s = re.sub('_+', '_', s)
    if s[0] in '0123456789':
        return '_' + s
    return s

def escape(s, escape_empty_string=True):
    ''' Shell escape `s` '''
    if not s and escape_empty_string is False: return ''
    if re.fullmatch('[a-zA-Z0-9_,:-]+', s): return s
    if "'" not in s: return "'%s'" % s
    if '"' not in s: return '"%s"' % s.replace('\\', '\\\\').replace('"', '\\"')
    return "'%s'" % s.replace("'", '\'"\'"\'')

def make_subparser_identifier(s):
    return make_identifier(f'_{s}_subcommands')

#def action_get_completion(action):
#    if hasattr(action, 'completion'):
#        return getattr(action, 'completion')
#
#    if action.choices:
#        if isinstance(action.choices, (list, tuple, set, dict)):
#            return ('choices', action.choices)
#
#        if isinstance(action.choices, range):
#            return ('range', action.choices)
#
#        raise Exception("Unknown type for choices: %r" % type(action.choices))
#
#    if action.takes_args():
#        if action.type not in (int, float):
#            return ('file',)
#
#    return ('none',)

class ShellCompleter:
    def complete(self, completion, *a, **kw):
        if not hasattr(self, completion):
            print("Warning: ShellCompleter: Falling back from `%s` to `none`" % (completion,), file=sys.stderr)
            completion = 'none'

        return getattr(self, completion)(*a, **kw)

    def fallback(self, from_, to, *a, **kw):
        print("Warning: ShellCompleter: Falling back from `%s` to `%s`" % (from_, to), file=sys.stderr)
        return self.complete(to, *a, **kw)

    def none(self):
        return ''

    def signal(self, prefix=''):
        ''' '''

        SIG = prefix
        signals = collections.OrderedDict([
            (SIG+'ABRT',   'Process abort signal'),
            (SIG+'ALRM',   'Alarm clock'),
            (SIG+'BUS',    'Access to an undefined portion of a memory object'),
            (SIG+'CHLD',   'Child process terminated, stopped, or continued'),
            (SIG+'CONT',   'Continue executing, if stopped'),
            (SIG+'FPE',    'Erroneous arithmetic operation'),
            (SIG+'HUP',    'Hangup'),
            (SIG+'ILL',    'Illegal instruction'),
            (SIG+'INT',    'Terminal interrupt signal'),
            (SIG+'KILL',   'Kill (cannot be caught or ignored)'),
            (SIG+'PIPE',   'Write on a pipe with no one to read it'),
            (SIG+'QUIT',   'Terminal quit signal'),
            (SIG+'SEGV',   'Invalid memory reference'),
            (SIG+'STOP',   'Stop executing (cannot be caught or ignored)'),
            (SIG+'TERM',   'Termination signal'),
            (SIG+'TSTP',   'Terminal stop signal'),
            (SIG+'TTIN',   'Background process attempting read'),
            (SIG+'TTOU',   'Background process attempting write'),
            (SIG+'USR1',   'User-defined signal 1'),
            (SIG+'USR2',   'User-defined signal 2'),
            (SIG+'POLL',   'Pollable event'),
            (SIG+'PROF',   'Profiling timer expired'),
            (SIG+'SYS',    'Bad system call'),
            (SIG+'TRAP',   'Trace/breakpoint trap'),
            (SIG+'XFSZ',   'File size limit exceeded'),
            (SIG+'VTALRM', 'Virtual timer expired'),
            (SIG+'XCPU',   'CPU time limit exceeded'),
        ])

        return self.complete('choices', signals)

    def range(self, _range):
        l = list(_range)

        if len(l) > 32:
            l = l[0:16] + ['...'] + l[-32:]

        return self.complete('choices', l)

    def directory(self, glob_pattern=None):
        return self.fallback('directory', 'file', glob_pattern)

    def process(self):
        return self.fallback('process', 'none')

    def pid(self):
        return self.fallback('pid', 'none')

    def command(self):
        return self.fallback('command', 'file')

    def variable(self):
        return self.fallback('variable', 'none')

    def service(self):
        return self.fallback('service', 'none')

    def user(self):
        return self.fallback('user', 'none')

    def group(self):
        return self.fallback('group', 'none')

