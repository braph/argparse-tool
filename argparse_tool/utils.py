#!/usr/bin/python3

import sys, argparse

# =============================================================================
# Utility functions
# =============================================================================

def action_complete(self, action, *a):
    setattr(self, 'completion', (action, *a))
    return self

argparse.Action.complete = action_complete
