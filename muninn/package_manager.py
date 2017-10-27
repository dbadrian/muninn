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

import muninn.builder as builder
import muninn.depresolver as depresolver
import muninn.packages as packages

logger = logging.getLogger(__name__)


class PackageManager():
    def __init__(self, pkg_dir):
        self.pkg_dir = os.path.abspath(pkg_dir)
        self.database_path = os.path.join(self.pkg_dir, ".database.json")
        self.is_initialized = self.__load_local_database()
        self.__scan_local_packages()

    def install_packages(self, desired_pkgs)
        # first load all other packages (=potential depdencies) as latest pkg
        gen = (x for x in self.pkgs.items() if x[0] not in desired_pkgs)
        for name, pkg in gen:
            pkg.load_module(version="latest")

        # now load all desired modules in desired version
        for pkg_name, version in desired_pkgs:
            self.pkgs["pkg"].load_module(version=version)

        depends_graph = depresolver.build_graph(self.pkgs)
        install_order = depresolver.resolve_graph(depends_graph)

        required_dependencies = set()
        missing_dependencies = set()
        skipped_packages = []
        desired_pkg_names = set([name for name, _ in desired_pkgs])
        for idx, pkg_name in enumerate(desired_pkg_names):
            # Recursively search and check what pkgs are required
            depends = set(
                depresolver.find_dependencies(pkg_name, depends_graph))

            if depends.issubset(
                    install_order):  # if depends can be satisfied
                # then collect those, which are not selected yet
                required_dependencies.update(
                    depends.difference(desired_pkg_names))
            else:
                missing_dependencies.update(
                    depends.difference(install_order))
                skipped_packages.append(pkg_name)
                logger.error("Dependencies ({}) can not be satisfied for {}"
                             .format(missing_dependencies, pkg_name))

        depends_msg = "The following packages are required as dependencies,\
                       and are automatically selected for installation."

        logger.info(depends_msg + " {}".format(required_dependencies))
        if skipped_packages:
            logger.info("Following packages will be skipped: {}"
                        .format(skipped_packages))

        if required_dependencies:
        # TODO: say some output or yes/no about the required dependncies
        # or pacman style, list all to installs

        for idx, pkg_name in enumerate(
                        list(desired_pkg_names) + list(required_dependencies)):
            if builder.install(self.pkgs[pkg_name]):
                self.database["installed"][pkg_name] = "latest"


    def initialize_new_database(self, overwrite=False):
        if os.path.isfile(self.database_path):
            logger.debug("Database already exists.")
            if overwrite:
                logger.debug("Overwriting database!")
            else:
                return False

        self.database = {
            "installed": {},
        }
        with open(self.database_path, 'w') as db_file:
            logger.debug("Creating empty database at %s.", self.database_path)
            json.dump(self.database, db_file, indent=4)

        self.is_initialized = True
        return True

    def __load_local_database(self):
        logger.debug("Loading package database from %s", self.database_path)
        try:
            with open(self.database_path, 'r') as db_file:
                self.database = json.load(db_file)
            return True
        except FileNotFoundError:
            logger.debug("Couldn't find package database. %s not initialized!",
                         self.__class__.__name__)
            return False

    def __save_local_database(self):
        if self.is_initialized:
            logger.debug("Saving database at %s", self.database_path)
            with open(self.database_path, 'w') as db_file:
                json.dump(self.database, db_file, indent=4)
        else:
            logger.debug("Database not initialized, not saving it!")

    def __scan_local_packages(self):
        # Search for packages
        pkg_paths = packages.search_packages(self.pkg_dir)

        # Load pkgs
        self.pkgs = {name: packages.Package(name, path) for (name, path) in
                     pkg_paths.items()}

        # Filter out invalid muninn pkgs
        # self.pkgs = {name: pkg for (name, pkg) in pkgs.items() if pkg.valid}
        # logger.debug("Valid muninn pkgs found: {}".format(self.pkgs))
