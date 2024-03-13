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
# Functions for getting information about an Action object
# =============================================================================

def action_complete(self, action, *a):
    setattr(self, 'completion', (action, *a))
    return self

argparse.Action.complete = action_complete
