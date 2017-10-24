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

import re
import os
import logging
import logging.config
import json
import errno
import types
import contextlib
import shutil
import tempfile
import inspect
import subprocess

try:
  from shutil import which
except ImportError:
  from distutils.spawn import find_executable as which

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


# Evil Python Stuff
def copy_func(f, name=None):
    return types.FunctionType(f.func_code, f.func_globals, name or f.func_name,
                              f.func_defaults, f.func_closure)


# OS/Path-related stuff
def get_current_module_folder():
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    return os.path.abspath(module.__file__).rsplit('/', 1)[0]

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def force_symlink(file1, file2):
    try:
        os.symlink(file1, file2)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(file2)
            os.symlink(file1, file2)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

@contextlib.contextmanager
def cd(newdir, cleanup=lambda: True):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
        cleanup()

@contextlib.contextmanager
def tempdir():
    dirpath = tempfile.mkdtemp()
    def cleanup():
        shutil.rmtree(dirpath)
    with cd(dirpath, cleanup):
        yield dirpath

# Text Processing
def extract_value_from_tags(text_input,
                            opening_tag="<!s>",
                            closing_tag="</!s>"):
    rstr = opening_tag + '(.*?)' + closing_tag

    return re.findall(rstr, text_input)


def replace_tags(text_input, key, value,
                 opening_tag="<!s>", closing_tag="</!s>"):
    # Not most efficient maybe, but okay for my simple use case
    return text_input.replace(opening_tag + key + closing_tag,  # Look For
                              value)                            # Replace by


# Git Interaction
def get_changed_files(repo):
    return [item.a_path for item in repo.index.diff(None)]

# System Interaction
def run_linux_cmd(cmd):
    subprocess.run(cmd.split())