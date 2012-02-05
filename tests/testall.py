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
ORIG_PORT = 8080
TEST_PORT = os.environ.get('TEST_PORT', ORIG_PORT)
TEST_PORT = int(TEST_PORT)


def doCommand(command):
    """A simple function that will run the given command string in the
    installer's working directory."""
    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            cwd=INSTALLER_ROOT,
                            shell=True)
    out, err = proc.communicate()
    return (out, err, proc.returncode)

#
# XXX Changing the ports sucks, but we have to do this here because the
#     changes elsewhere would be somewhat drastic. And we need to change
#     the port because there is an off chance that it will collide with
#     another service on the same port.
#
_files_and_modifiers = [('../helper_scripts/create_instance.py', 'BASE_ADDRESS = %s'),
                        ('../buildout_templates/cluster.cfg', 'http-address = %s'),
                        ('../buildout_templates/standalone.cfg', 'http-address = %s'),
                        ]
_mod_extension = '.orig'
_has_been_modified = False
def changePorts():
    """Change the configured ports so that they don't collide with
    some other running service."""
    if TEST_PORT == ORIG_PORT:
        return  # Default, no need to change anything...
    else:
        _has_been_modified = True
    for file, rline in _files_and_modifiers:
        replace_this = rline % ORIG_PORT
        replacement = rline % TEST_PORT
        # Make a copy of the current file for later restoration.
        file_clone = file + _mod_extension
        shutil.copy2(file, file_clone)
        with open(file, 'w') as script:
            content = open(file_clone).read().replace(replace_this, replacement)
            script.write(content)
def revertPorts():
    """Change the adjusted ports configuration back to the original state."""
    if not _has_been_modified:
        return
    # Restore the originals...
    for file, rline in _files_and_modifiers:
        file_clone = file + _mod_extension
        shutil.copy2(file_clone, file)
#
# /XXX
#

# Note: Check your tempfile.gettempdir() path length if you get
#       'AF_UNIX path to long' errors.
_testTarget = tempfile.mkdtemp()
DOCTEST_GLOBALS = {
    'doCommand': doCommand,
    'withClientPort': TEST_PORT,
    'testTarget': _testTarget,
    'withPython': sys.executable,
    }

optionflags = doctest.ELLIPSIS or NORMALIZE_WHITESPACE


changePorts()
try:
    doctest.testfile("tests.txt",
                     optionflags=optionflags,
                     globs=DOCTEST_GLOBALS,
                     )
finally:
    revertPorts()
    # Clean up
    shutil.rmtree(_testTarget)

sys.exit(0)
