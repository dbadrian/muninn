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
import glob
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


# Evil Python Stuff
def copy_func(f, name=None):
    return types.FunctionType(f.func_code, f.func_globals, name or f.func_name,
                              f.func_defaults, f.func_closure)


# OS/Path-related stuff
def glob_files(base_path, relative_targets):
    fn_queue = []
    for target in relative_targets:
        path_origin = os.path.join(base_path, target)
        # process unix style wildcards
        for file in glob.glob(path_origin):
            fn_queue.append(file.rsplit("/", 1)[1])
    return fn_queue


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
def get_non_comment_lines(text):
    pure_text = []
    for line in text.split('\n'):
        li = line.strip()
        if not li.startswith("#"):
            pure_text.append(line.rstrip())
    # return result without any empty lines
    return [line for line in pure_text if line]


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
try:
    from git import Repo


    def get_changed_files(repo_path):
        repo = Repo(repo_path)
        return [item.a_path for item in repo.index.diff(None)]


    def get_untracked_files(repo_path):
        repo = Repo(repo_path)
        return repo.untracked_files


    def stage_files(repo_path, relative_file_paths):
        repo = Repo(repo_path)
        abs_file_paths = [os.path.join(repo.working_tree_dir, p) for p in
                          relative_file_paths]
        for file in abs_file_paths:
            if os.path.isfile(file):
                repo.index.add([file])
            else:
                repo.index.remove([file])


    def unstage_files(repo_path, relative_file_paths):
        repo = Repo(repo_path)
        repo.index.reset(commit="HEAD", paths=relative_file_paths)


    def push(repo_path, local_branch="master", remote="origin"):
        repo = Repo(repo_path)
        return repo.git.push(remote, local_branch)


    def commit(repo_path, message):
        repo = Repo(repo_path)
        repo.git.commit(m=message)


except ModuleNotFoundError:
    def get_changed_files(repo):
        raise NotImplementedError


    def get_untracked_files(repo_path):
        raise NotImplementedError


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


# muninn
def bump_version(version, major=False, minor=False, patch=True):
    ma, mi, pa = map(int, version.split('.'))
    if major: ma += 1
    if minor: mi += 1
    if patch: pa += 1
    return '.'.join([str(ma), str(mi), str(pa)])

def make_pkg_string(pkg):
# [(pkg.info["name"], pkg.info["desc"], False)
#                for pkg in pkgs.values()]
    pkg_deps = " ".join(pkg.info["depends"]["muninn"]) if pkg.info["depends"]["muninn"] else "*None*"
    base_pkg_string = str(pkg.info["name"]) + " | " \
                     + str(pkg.info["version"])  +" | " \
                     + str(pkg.info["desc"]) + " | " \
                     + pkg_deps + "\n"
    return base_pkg_string


def generate_supported_pkgs_string(pkgs):
    table_str = "Package Name | Version | Description | Dependencies Muninn\n--- | --- | --- | --- \n"
    for (name, pkg) in sorted(pkgs.items()):
        table_str += make_pkg_string(pkg)

    return table_str

# useful python snippets
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
