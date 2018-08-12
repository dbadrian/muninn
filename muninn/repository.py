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
import datetime
import time
from pathlib import Path

from git import Repo
from git.exc import InvalidGitRepositoryError

import muninn.common as common
import muninn.package as packages

logger = logging.getLogger(__name__)


class Repository():
    def __init__(self, repository_path):
        self.path = Path(repository_path).expanduser()
        self.db_path = self.path.joinpath("db.json")

        # Make sure it is a correct repository
        if not self.path.exists():
            logger.error("Repository Path: {} does not exist.".format(repository_path))
            self.initialized = False
        # elif not self.db_path.is_file():
        #     logger.error("Repository database missing. Maybe not initialized yet?")
        else:
            # All good!
            # self.db = self.load_repository()
            # self.initialized = True
            self.repo = Repo(str(self.path))
            logger.debug("Repo loaded")
            return

        self.initialized = False

    def load_repository(self):
        if self.initialized:
            db = json.load(os.path.join(self.path, "db.json"))
            return db
        else:
            logger.error("Repository not yet initialized. Please initalize first!")

    def initialize_repository(self):
        """Reinitializing won't really hurt, and will just stop early returning true"""
        logger.info("Initializing muninn repository at '{}'".format(str(self.path)))

        # Create Folder
        self.path.mkdir(parents=True, exist_ok=True)

        # Init the git repo (again if it already exists...doesnt hurt)
        try:
            Repo(str(self.path))
            logger.debug("Repository already exists. Manually rebuild database if desired!")
            return True
        except InvalidGitRepositoryError:
            repo = Repo.init(str(self.path))

        # Add and commit gitignore
        self.__copy_gitignore()
        common.stage_and_commit_files(repo, str(self.path.joinpath(".gitignore")),".gitignore base")
        repo.create_tag("repo/initialization")

        # Generate (new) database
        self.__rebuild_database()

        self.initialized = True
        return True

    def add_remote(self, url, name='origin'):
        pass

    def list_remotes(self):
        pass

    def remove_remotes(self, name='origin'):
        pass

    ############################################################################
    ################### PACKAGE MANAGEMENT #####################################
    ############################################################################

    def add_new_package(self, name):
        # create subfolder
        # create the py base file
        # make no committ though
        pass

    def list_untracked_packages(self):
        # difference of subfolders and tracked packagers (sets)
        tracked_pkgs = set(self.get_tracked_packages())
        pkgs = set(self.__search_package_candidates().keys())
        list(pkgs.difference(tracked_pkgs))

    def start_tracking_package(self, name):
        self.__commit_package(name, "{}: Tracking Activated".format(name))

    def update_package(self, name):
        self.__commit_package(name, "{}: Update".format(name))


    def rollback_package(self, name, desired_version):
        #SHOULD ONLY BE RUN IF THE PACKAGE IS NOT INSTALLED!
        # verify if package is clean, if not: update package
        # checkout procedure

        # If module is already at the correct version, do nothing
        current_pkg_rev = self.current_package_revision()
        if desired_version == current_pkg_rev:
            logger.debug("Current Package version is the same as desired. Aborting.")
            return True

        # Else check if there are currently untracked changes
        changed_files, untracked_files = self.check_package_status(name)

        if changed_files:
            pass # do something

        if untracked_files:
            pass # do something

        # If package is now clean and commited
        # `````````````````````````````````````````````````````
        # 1. Create temporary directory $tempdir
        # 2. git archive $TAG:$NAME | tar x -C $tempdir
        # 3. rm -r $REPO/$NAME/*
        # 4. cp -ar $tempdir/* $REPO/$NAME
        # 5. delete $tempdir
        # 6. git commit --allow-empty the package
        # `````````````````````````````````````````````````````
        pass

    def current_package_revision(self, name):
        return self.get_package_revisions(name)[-1]

    def get_package_revisions(self, name):
        revisions = self.repo.git.tag('--list', "{}/*".format(name)).split('\n')
        revisions = list({rev.split("/")[1] for rev in revisions })
        return sorted(revisions)


    def get_tracked_packages(self):
        tags= [str(tag) for tag in  self.repo.tags]
        pkgs = {tag.split("/")[0] for tag in tags}
        pkgs.remove("repo")
        return list(pkgs)

    def check_package_status(self, name=""):
        changed_files = common.get_changed_files(self.repo)
        untracked_files = common.get_untracked_files(self.repo)

        if name:
            changed_files = [file for file in changed_files if file.split(os.sep)[0] == name]
            untracked_files = [file for file in untracked_files if file.split(os.sep)[0] == name]

        return changed_files, untracked_files


    def __commit_package(self, name, message):
        p_pkg = str(self.path.joinpath(name))
        common.stage_and_commit_files(self.repo, p_pkg, message)
        self.repo.create_tag("{}/{}".format(name, self.__timestamp()))


    ############################################################################
    ################### DATABASE & REPOSITORY ##################################
    ############################################################################

    def __update_repo_files(self):
        # like gitignore???
        pass

    def __rebuild_database(self):
        logger.debug("Rebuilding database")
        # Search for packages
        pkg_candidates = self.__search_package_candidates()

        # Load pkgs
        pkgs = {name: packages.load_package(path, name) for (name, path) in pkg_candidates.items()}

        # Filter out invalid muninn pkgs
        self.pkgs = {name: pkg for (name, pkg) in pkgs.items() if pkg().valid}
        self.invalid_pkgs = {name: pkg for (name, pkg) in pkgs.items() if not pkg().valid}
        logger.debug("Valid muninn pkgs found: {}".format(self.pkgs))


        # TODO: Add and commit got git repo
        # if self.db_path.is_file():
        #     logger.debug("Existing database will be renamed to .db.json.bak (hidden file)")
        #     self.db_path.rename(self.path.joinpath(".db.json.bak"))
        #
        # # Write new database
        # self.__write_database()

    def __search_package_candidates(self):
        logger.debug(
            "Scanning repository for packages in: '{}'".format(str(self.path)))

        # Aggregate potential packages by finding all subdirectories in repository
        pkg_candidates = common.get_immediate_subdirectories(self.path)
        logger.debug("Package Candidates %s", pkg_candidates)

        # Check if they contain a python file of same name
        packages = {pkg_candidate: os.path.join(self.path, pkg_candidate) for
                    pkg_candidate in pkg_candidates if os.path.exists(
            os.path.join(self.path, pkg_candidate, pkg_candidate + ".py"))}

        logger.info("Found %i packages: %s", len(packages), packages)
        return packages

    def __write_database(self):
        pass


    def __copy_gitignore(self):
        filep = os.path.join(common.muninn_module_path(), "templates", "repo_gitignore")
        shutil.copyfile(filep, self.path.joinpath(".gitignore"))

    def __timestamp(self):
        return datetime.datetime.fromtimestamp(time.time()).strftime('%y%m%d-%H%M%S')