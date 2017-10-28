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

import contextlib
import errno
import inspect
import json
import logging
import logging.config
import os
import re
import shutil
import subprocess
import tempfile
import types

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
                              value)  # Replace by


def get_params(fn_sample):
    if not os.path.exists(fn_sample):
        logger.error("\"%s\" does not exist. Can't load sample file.",
                     fn_sample)
        return None
    else:
        with open(fn_sample, 'r') as f_sample:
            d_sample = f_sample.read()
            return extract_value_from_tags(d_sample)


# Git Interaction
def get_changed_files(repo):
    # requires gitpython
    return [item.a_path for item in repo.index.diff(None)]


def get_latest_commit(path):
    cmd = "git log -n 1 --pretty=format:%H -- {}".format(path)
    return run_linux_cmd(cmd, stdout=True, cwd=path).stdout


def get_commits(path, n_commits=-1):
    cmd = "git log -n {} --pretty=format:%H -- {}".format(n_commits, path)
    return run_linux_cmd(cmd, stdout=True, cwd=path).stdout.decode(
        "utf-8").split("\n")


def checkout_path_at_commit(path, commit, out_path):
    if not os.path.isdir(out_path):
        logger.debug("Output folder does not exit, aborting checkout.")
        return

    # git archive returns a tar'd version of cwd at commit
    cmd_git = "git archive --format tar {}".format(commit)
    sp = subprocess.run(cmd_git.split(), stdout=subprocess.PIPE, cwd=path)
    # we untar the result to the out_path, second command to avoid shell=True for pipe
    cmd_tar = "tar x -C {}".format(out_path)
    subprocess.run(cmd_tar.split(), input=sp.stdout, cwd=path)


def get_file_at_commit(path, commit):
    path, filename = os.path.split(path)
    cmd = "git show {}:{}".format(commit, "./" + filename)
    return run_linux_cmd(cmd, True, path).stdout.decode("utf-8")


# System Interaction
def run_linux_cmd(cmd, stdout=True, cwd=None, shell=False):
    if stdout:
        return subprocess.run(cmd.split(), stdout=subprocess.PIPE, cwd=cwd,
                              shell=shell)
    else:
        return subprocess.run(cmd.split(), cwd=cwd, shell=shell)


# useful python snippets
def yes_or_no(question):
    reply = str(input(question+' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter a correct one...")
