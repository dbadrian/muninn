import io
import os
import subprocess
import tarfile

from muninn.common import message_from_sys_editor, run_linux_cmd, logger
from muninn.text import get_non_comment_lines


def git_file_choose_dialog(changed_files, untracked_files):
    # generate text with grouping by packages and list modified and untracked
    # files. everything without a hashtag will be added to comming up commit.
    pkg_msg = "# Change Type: {}\n" \
              "{}\n\n"

    msg = "############################################################\n" \
          "# Please confirm the changes that will be recorded in the \n" \
          "# commit. Lines starting with '#' will be ignored.\n" \
          "# ’A’ for added paths\n" \
          "# ’D’ for deleted paths\n" \
          "# ’R’ for renamed paths\n" \
          "# ’M’ for paths with modified data\n" \
          "# ’T’ for changed in the type paths\n" \
          "############################################################\n\n"

    change_types = {ctype for _, ctype in changed_files}
    for ct in change_types:
        s_changed = "\n".join([file for file, ctype in changed_files if ctype == ct])
        msg += pkg_msg.format(ct, s_changed)

    s_untracked = "\n".join([file for file in untracked_files])
    msg += pkg_msg.format("Untracked", s_untracked)

    ret = message_from_sys_editor(msg)
    files_to_stage = get_non_comment_lines(ret)

    return files_to_stage


def get_changed_files(repo):
    diff = []
    idx_diff = repo.index.diff(None)
    for change_type in idx_diff.change_type:
        for file in idx_diff.iter_change_type(change_type):
            diff.append((file.a_path, change_type))

    return diff


def get_untracked_files(repo):
    return repo.untracked_files


def stage_files_absolute(repo, absolute_file_paths):
    absolute_file_paths = [absolute_file_paths] if type(absolute_file_paths) == str else absolute_file_paths
    for file in absolute_file_paths:
        if os.path.exists(file):
            repo.index.add([file])
        else:
            repo.index.remove([file])


def get_absolute_paths(repo, relative_file_paths):
    return [os.path.join(repo.working_tree_dir, p) for p in relative_file_paths]


def unstage_files(repo_path, relative_file_paths):
    repo = Repo(repo_path)
    repo.index.reset(commit="HEAD", paths=relative_file_paths)


def push(repo_path, local_branch="master", remote="origin"):
    repo = Repo(repo_path)
    return repo.git.push(remote, local_branch)


def commit(repo, message):
    repo.git.commit(m=message)


def stage_and_commit_files(repo, abs_file_paths, message):
    stage_files_absolute(repo, abs_file_paths)
    commit(repo, message)


def restore_path_at_tag(repo, tag, path_in_repository, restore_path):
    # cmd = "git archive {}:{} | tar x -C {}".format(tag, path_in_repository,
    #                                                restore_path)
    # print(cmd)
    # run_linux_cmd(cmd)
    tar_str = repo.git.archive("{}:{}".format(tag, path_in_repository))
    tar_file = io.BytesIO(tar_str.encode('utf-8'))
    with tarfile.open(mode="r", fileobj=tar_file) as f:
        f.extractall(restore_path)


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