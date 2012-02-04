#!/usr/bin/env python
"""\
Test the build installs as expected.

Run with environment the TMPDIR environment variable set to keep the
temporary build with your user space. For example:

    $ TMPDIR=~/tmp python testall.py

"""
import os
import sys
import subprocess
import tempfile
import shutil
import doctest


HERE = os.path.dirname(__file__)
INSTALLER_ROOT = os.path.abspath(os.path.join(HERE, '..'))

def doCommand(command):
    """A simple function that will run the given command string in the
    installer's working directory."""
    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            cwd=INSTALLER_ROOT,
                            shell=True)
    out, err = proc.communicate()
    return (out, err, proc.returncode)

# Note: Check your tempfile.gettempdir() path length if you get
#       'AF_UNIX path to long' errors.
_testTarget = tempfile.mkdtemp()
DOCTEST_GLOBALS = {
    'doCommand': doCommand,
    'testTarget': _testTarget,
    'withPython': sys.executable,
    }

optionflags = doctest.ELLIPSIS or NORMALIZE_WHITESPACE

doctest.testfile("tests.txt",
                 optionflags=optionflags,
                 globs=DOCTEST_GLOBALS,
                 )

# Clean up
shutil.rmtree(_testTarget)
sys.exit(0)
