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

import json
import logging
import os
import shutil
from pathlib import Path

from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError

import muninn.common as common
import muninn.fs
import muninn.git
import muninn.exceptions as exc

logger = logging.getLogger(__name__)


class Repository():
    def __init__(self, repository_path=None):

        if repository_path:
            self.path = Path(repository_path)
        elif os.environ.get('MUNINN_REPOSITORY'):
            self.path = Path(os.environ.get('MUNINN_REPOSITORY')).expanduser()
        else:
            logger.error("No path to muninn repository defined. Set environment variable MUNINN_DB or give explicitly.")
            raise exc.RepositoryInvalidDBPath

        try:
            if self.path.exists():
                self.repo = Repo(str(self.path))
                logger.debug("Repository loaded.")
                self.initialized = True
            else:
                raise Exception
        except:
            logger.error("Repository could not be loaded. Already initialized?")
            self.initialized = False

    ############################################################################
    ################### PACKAGE MAINTANCE ######################################
    ############################################################################

    def add_empty_package(self, name):
        """
        Creates an "empty" package, which does nothing, but has all the
        import base files and sub-folders. Returns true on success.
        Will not be tracked yet! Needs to be marked for release first.
        """
        pkgpath = self.path.joinpath(name)
        if pkgpath.exists():
            logger.error(
                "A package with the same name ({}) already exists. Aborting.".format(
                    name))
            return False

        # create subfolder
        pkgpath.mkdir()
        pkgpath.joinpath("_pkg_data").mkdir()
        # create the py base file
        self.__copy_package_base(name)

        return True

    def start_tracking_package(self, name):
        if not name in self.get_tracked_packages():
            return self.__commit_package(name, "{}: Tracking Activated".format(name))
        else:
            logger.debug("Package {} already being tracked.".format(name))

    def update_package(self, name):
        return self.__commit_package(name, "{}: Update".format(name))

    def rollback_package(self, name, desired_version):
        # If module is already at the correct version, do nothing
        current_pkg_rev = self.current_package_revision(name)
        if desired_version == current_pkg_rev:
            logger.debug(
                "Current Package version is the same as desired. Aborting.")
            return True

        changed_files, untracked_files = self.check_package_status(name)
        if changed_files or untracked_files:
            logger.error(
                "Package status is not clean (uncommitted or untracked files). Resolve first!")
            return False

        with muninn.fs.tempdir() as tdir:
            # Restore the path at the given tag
            tag = "{}/{}/update".format(name, desired_version)
            muninn.git.restore_path_at_tag(self.repo, tag, name, tdir)

            # Delete the current folder & and recreate since its easier...
            pkg_path = self.path.joinpath(name)
            shutil.rmtree(pkg_path)

            # Copy the restored folder
            shutil.copytree(Path(tdir), pkg_path)

            # And commit accordingly
            self.__commit_package(name, "{}: Rollback to {}".format(name,
                                                                    desired_version),
                                  "rollback_from/{}".format(desired_version))

        return True

    def current_package_revision(self, name):
        tag = self.repo.git.describe("--match", "{}/*".format(name), "--tags", "HEAD")
        tag = tag.split("/")
        if tag[2] == "update":
            return tag[1]
        elif tag[2] == "rollback_from":
            return tag[3]
        else:
            raise NotImplementedError

    def get_package_revisions(self, name):
        revisions = self.repo.git.tag('--list', "{}/*".format(name)).split('\n')
        revisions = [rev.split("/") for rev in revisions]
        revisions = {rev[1] for rev in revisions if rev[2] == "update"}
        return sorted(revisions)

    def get_tracked_packages(self):
        tags = [str(tag) for tag in self.repo.tags]
        pkgs = {tag.split("/")[0] for tag in tags}
        pkgs.remove("repo")
        return pkgs

    def list_untracked_packages(self):
        # difference of sub-folders and tracked packagers (sets)
        tracked_pkgs = set(self.get_tracked_packages())
        pkgs = set(self.__search_package_candidates().keys())
        list(pkgs.difference(tracked_pkgs))

    def check_package_status(self, name=""):
        changed_files = muninn.git.get_changed_files(self.repo)
        untracked_files = muninn.git.get_untracked_files(self.repo)

        if name:
            changed_files = [(file, ctype) for file, ctype in changed_files if
                             file.split(os.sep)[0] == name]
            untracked_files = [file for file in untracked_files if
                               file.split(os.sep)[0] == name]

        return changed_files, untracked_files

    def modified_packages(self):
        # get all modified files
        cf, _ = self.check_package_status()
        pkgs = {file[0].split("/")[0] for file in cf}
        return pkgs

    def __commit_package(self, pkg_name, message, commit_type="update",
                         file_selector=True):
        files = muninn.git.git_file_choose_dialog(
            *self.check_package_status(pkg_name)) if file_selector else [
            pkg_name]

        files = [str(self.path.joinpath(file)) for file in files]

        if files:
            muninn.git.stage_and_commit_files(self.repo, files, message)
            ts = common.timestamp()
            self.repo.create_tag(
                "{}/{}/{}".format(pkg_name, ts, commit_type))
            return ts
        else:
            logger.debug("Nothing to commit, skipping.")

    def __update_repo_files(self):
        # like gitignore???
        pass

    def __copy_gitignore(self):
        filep = os.path.join(common.muninn_module_path(), "templates",
                             "repo_gitignore")
        shutil.copyfile(filep, self.path.joinpath(".gitignore"))

    def __copy_package_base(self, pkg_name):
        filep = os.path.join(common.muninn_module_path(), "templates",
                             "package_base")
        shutil.copyfile(filep, self.path.joinpath("{}".format(pkg_name),
                                                  "{}.py".format(pkg_name)))

    ############################################################################
    ################### DATABASE & REPOSITORY ##################################
    ############################################################################

    def load_repository(self):
        if self.initialized:
            db = json.load(os.path.join(self.path, "db.json"))
            return db
        else:
            logger.error(
                "Repository not yet initialized. Please initalize first!")

    def initialize_repository(self):
        """Reinitializing won't really hurt, and will just stop early returning true"""
        logger.info(
            "Initializing muninn repository at '{}'".format(str(self.path)))

        # Create Folder
        self.path.mkdir(parents=True, exist_ok=True)

        # Init the git repo (again if it already exists...doesnt hurt)
        try:
            self.repo = Repo(str(self.path))
            logger.debug(
                "Repository already exists. Manually rebuild database if desired!")
            return True
        except InvalidGitRepositoryError:
            self.repo = Repo.init(str(self.path))

        # Add and commit gitignore
        self.__copy_gitignore()
        muninn.git.stage_and_commit_files(self.repo,
                                          str(self.path.joinpath(".gitignore")),
                                      ".gitignore base")
        self.repo.create_tag("repo/initialization")

        self.initialized = True
        return True

    def list_remotes(self):
        return {remote.name for remote in repo.remotes}

    def add_remote(self, remote, url):
        if not remote in self.list_remotes():
            return self.repo.create_remote(remote, url)
        else:
            raise exc.RepositoryRemoteAlreadyExists

    def delete_remote(self, remote):
        if remote in self.list_remotes():
            return self.repo.delete_remote(remote)
        else:
            raise exc.RepositoryRemoteDoesNotExists

    def pull(self, remote='origin'):
        # if remote in self.repo.remotes:
        try:
            self.repo.remotes[remote].pull()
        except GitCommandError:
            # call mergetool?
            self.repo.git.mergetool()
            if common.yes_or_no("Merge finished? Yes, will commit changes!"):
                self.repo.git.reset()
                dirty_pkgs = self.modified_packages()
                for pkg in dirty_pkgs:
                    self.__commit_package(pkg, "{}: Merge".format(pkg), "update/merge")
        except IndexError:
            logger.error("Remote {} does not exit.".format(remote))
            raise exc.RepositoryRemoteDoesNotExists

    def push(self, remote='origin'):
        try:
            self.repo.remotes[remote].push()
        except GitCommandError:
            logger.error("Push rejected. Check if URL is accessible, or trying pulling first and resolve any merge conflicts.")
            raise exc.RepositoryRemotePushConflict
        except IndexError:
            logger.error("Remote {} does not exit.".format(remote))
            raise exc.RepositoryRemoteDoesNotExists