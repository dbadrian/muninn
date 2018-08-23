import contextlib
import errno
import glob
import inspect
import os
import shutil
import tempfile


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