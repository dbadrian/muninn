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
from pathlib import Path

import muninn.repository as repo
import muninn.package as packages
import muninn.exceptions as exc
import muninn.fs as fs



logger = logging.getLogger(__name__)


class PackageManager():
    def __init__(self, package_manager_db_path=None):
        if package_manager_db_path:
            self.path = Path(package_manager_db_path).expanduser()
        elif os.environ.get('MUNINN_DB'):
            self.path = Path(os.environ.get('MUNINN_DB')).expanduser()
        else:
            logger.error("No path to muninn db path defined. Set environment variable MUNINN_DB or give explicitly.")
            raise exc.PackageManagerInvalidDBPath


        if self.path.exists():
            self.__load_db()
        else:
            self.initialized = False
            logger.error("Path to packager manager db not found! Is it initalized?")
            raise exc.PackageManagerDBNotFound

    def initialize(self, repo_path):
        if self.path.exists():
            logger.error("Package Manager DB seems to already exits. Aborting initialization.")
            raise exc.PackageManagerDBAlreadyExists

        self.path.mkdir()
        db = {
            "repository_path": repo_path
        }
        with open(self.path, "w") as f:
            json.dump(db, f, indent=4)

    def __load_db(self):
        with open(self.path, "r") as f:
            self.db = json.load(f)
        self.initialized = True

    def __load_packages(self):
        # Search for packages
        pkg_candidates = self.__search_package_candidates()

        # Load pkgs
        pkgs = {name: packages.load_package(path, name) for (name, path) in
                pkg_candidates.items()}

        # Filter out invalid muninn pkgs
        self.pkgs = {name: pkg for (name, pkg) in pkgs.items() if pkg().valid}
        logger.debug("Valid muninn pkgs found: {}".format(self.pkgs.keys()))

        self.invalid_pkgs = {name for name, pkg in pkgs.items() if
                             not pkg().valid}
        logger.debug("Invalid muninn pkgs found: {}".format(self.pkgs))


    def __search_package_candidates(self):
        logger.debug(
            "Scanning repository for packages in: '{}'".format(str(self.path)))

        # Aggregate potential packages by finding all subdirectories in repository
        pkg_candidates = fs.get_immediate_subdirectories(self.path)
        logger.debug("Package Candidates %s", pkg_candidates)

        # Check if they contain a python file of same name
        packages = {pkg_candidate: os.path.join(self.path, pkg_candidate) for
                    pkg_candidate in pkg_candidates if os.path.exists(
            os.path.join(self.path, pkg_candidate, pkg_candidate + ".py"))}

        logger.info("Found %i packages: %s", len(packages), packages)
        return packages

    def __write_database(self):
        pass