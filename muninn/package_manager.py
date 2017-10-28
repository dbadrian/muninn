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
        self.__scan_repository()

    def install_packages(self, desired_pkgs, dry_run=False,
                         force_reinstall=False):
        # check if desired packages exist
        filtered_pkgs = [pkg_blob for pkg_blob in desired_pkgs if
                         pkg_blob[0] in self.pkgs]
        dropped_pkgs = set(desired_pkgs).difference(set(filtered_pkgs))
        if dropped_pkgs:
            msg = ''.join(
                ["    " + str(idx) + ": " + pkg_name + "\n" for
                 idx, (pkg_name, _) in
                 enumerate(dropped_pkgs)])
            logger.info(
                "Following packages do not exit and will be skipped: \n%s", msg)

        pkg2ver = {name: version for name, version in filtered_pkgs}

        # now load all desired modules in desired version
        for pkg_name, version in filtered_pkgs:
            logger.debug("Loading module: %s", pkg_name)
            self.pkgs[pkg_name].load_module(version=version)

        depends_graph, removed_pkgs = depresolver.build_graph(filtered_pkgs,
                                                              self.pkgs)
        install_order = depresolver.resolve_graph(depends_graph)


        if not force_reinstall:
            logger.debug("Filtering packages by: 'already installed' and 'up2date'")
            install_order = [pkg for pkg in install_order if
                             pkg not in self.database["installed"] or
                             self.database["installed"][pkg] != "latest"]

        logger.info(
            "Following packages (and required dependencies will be installed: "
            "%s",
            install_order)
        if removed_pkgs:
            logger.info(
                "Following packages (and dependencies) will not be installed "
                "because of unresolved dependencies %s",
                removed_pkgs)

        print("FINAL SELECTION:", install_order)
        if not dry_run:
            for idx, pkg_name in enumerate(install_order):
                if builder.install(self.pkgs[pkg_name]):
                    self.database["installed"][pkg_name] = pkg2ver[pkg_name]
                else:
                    return 1  # Failed installing a package. Abort!

        self.__save_local_database()
        return 0  # Successfully installed all packages

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
            return self.initialize_new_database()

    def __save_local_database(self):
        if self.is_initialized:
            logger.debug("Saving database at %s", self.database_path)
            with open(self.database_path, 'w') as db_file:
                json.dump(self.database, db_file, indent=4)
        else:
            logger.debug("Database not initialized, not saving it!")

    def __scan_repository(self):
        # Search for packages
        pkg_paths = packages.search_packages(self.pkg_dir)

        # Load pkgs
        self.pkgs = {name: packages.Package(name, path) for (name, path) in
                     pkg_paths.items()}

        # Filter out invalid muninn pkgs
        # self.pkgs = {name: pkg for (name, pkg) in pkgs.items() if pkg.valid}
        # logger.debug("Valid muninn pkgs found: {}".format(self.pkgs))