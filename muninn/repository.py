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


import muninn.common as common
import muninn.packages as packages

logger = logging.getLogger(__name__)


class Repository():
    def __init__(self, repository_path):
        self.path = Path(repository_path).expanduser()
        self.db_path = self.path.joinpath("db.json")

        # Make sure it is a correct repository
        if not self.path.exists(repository_path):
            logger.error("Repository Path: {} does not exist.".format(repository_path))
            self.initialized = False
        elif not self.db_path.is_file():
            logger.error("Repository database missing. Maybe not initialized yet?")
        else:
            # All good!
            self.db = self.load_repository()
            self.initialized = True
            return

        self.initialized = False

    def load_repository(self):
        if self.initialized:
            db = json.load(os.path.join(self.path, "db.json"))
            return db
        else:
            logger.error("Repository not yet initialized. Please initalize first!")

    def __initialize_repository(self):
        self.path.mkdir(parents=True, exist_ok=False)
        self.__rebuild_database()

    def __rebuild_database(self):
        logger.debug("Rebuilding database")
        # Search for packages
        pkg_candidates = packages.__search_package_candidates(self.pkg_dir)

        # Load pkgs
        pkgs = {name: packages.Package(name, path) for (name, path) in pkg_candidates.items()}

        # Filter out invalid muninn pkgs
        self.pkgs = {name: pkg for (name, pkg) in pkgs.items() if pkg.valid}
        self.invalid_pkgs = {name: pkg for (name, pkg) in pkgs.items() if not pkg.valid}
        logger.debug("Valid muninn pkgs found: {}".format(self.pkgs))

        if self.db_path.is_file():
            logger.debug("Existing database will be renamed to .db.json.bak (hidden file)")
            self.db_path.rename(self.path.joinpath(".db.json.bak"))

        # Write new database
        self.__write_database()

    def __search_package_candidates(self):
        logger.debug(
            "Scanning repository for packages in (Path: {}".format(self.path))

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