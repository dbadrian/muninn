#     Muninn: A python-powered dotfile manager with extras.
#     Copyright (C) 2017  David B. Adrian
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime
import json
import logging
import logging.config
import os
import subprocess
import tempfile
import time
from subprocess import call

try:
    from shutil import which
except ImportError:
    from distutils.spawn import find_executable as which

logger = logging.getLogger(__name__)


# Logging
def setup_logging(
        path='logger.json',
        level=logging.INFO,
        env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=level)


# Some Muninn Things
def yes_or_no(question):
    reply = str(input(question + ' (y/n): ')).lower().strip()
    if len(reply) > 0:
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False

    return yes_or_no("Uhhhh... please enter a correct one...")


def message_from_sys_editor(initial_message=""):
    EDITOR = os.environ.get('EDITOR', 'nano')  # that easy!

    initial_message = initial_message.encode('utf-8')

    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        tf.write(initial_message)
        tf.flush()
        call([EDITOR, tf.name])

        # do the parsing with `tf` using regular File operations.
        # for instance:
        tf.seek(0)
        return tf.read().decode('utf-8')

def muninn_module_path():
    path = os.path.abspath(__file__)
    return os.path.dirname(path)


def timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%y%m%d-%H%M%S')


# System Interaction
def run_linux_cmd(cmd, stdout=True, cwd=None, shell=False):
    if stdout:
        return subprocess.run(cmd.split(), stdout=subprocess.PIPE, cwd=cwd,
                              shell=shell)
    else:
        return subprocess.run(cmd.split(), cwd=cwd, shell=shell)

def run_script(script, stdin=None, shell='bash'):
    """Returns (stdout, stderr), raises error on non-zero return code"""
    import subprocess
    # Note: by using a list here (['bash', ...]) you avoid quoting issues, as the
    # arguments are passed in exactly this order (spaces, quotes, and newlines won't
    # cause problems):
    proc = subprocess.Popen([shell, '-c', script],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        stdin=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode:
        raise ScriptException(proc.returncode, stdout, stderr, script)
    return stdout, stderr


class ScriptException(Exception):
    def __init__(self, returncode, stdout, stderr, script):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        Exception.__init__('Error in script')

# muninn: mostly deprecated
def bump_version(version, major=False, minor=False, patch=True):
    ma, mi, pa = map(int, version.split('.'))
    if major: ma += 1
    if minor: mi += 1
    if patch: pa += 1
    return '.'.join([str(ma), str(mi), str(pa)])

def make_pkg_string(pkg):
# [(pkg.info["name"], pkg.info["description"], False)
#                for pkg in pkgs.values()]
    pkg_deps = " ".join(pkg.info["depends"]["muninn"]) if pkg.info["depends"]["muninn"] else "*None*"
    base_pkg_string = str(pkg.info["name"]) + " | " \
                     + str(pkg.info["version"])  +" | " \
                     + str(pkg.info["description"]) + " | " \
                     + pkg_deps + "\n"
    return base_pkg_string


def generate_supported_pkgs_string(pkgs):
    table_str = "Package Name | Version | Description | Dependencies Muninn\n--- | --- | --- | --- \n"
    for (name, pkg) in sorted(pkgs.items()):
        table_str += make_pkg_string(pkg)

    return table_str