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

logger = logging.getLogger(__name__)


class PackageDatabase():
    def __init__(self, pkg_dir):
        self.database_path = os.path.join(pkg_dir, ".database.json")
        self.is_initialized = self.__load_database()

    def initialize_new_database(self, overwrite=False):
        if os.path.isfile(self.database_path):
            logger.debug("Database already exists.")
            if overwrite:
                logger.debug("Overwriting database!")
            else:
                return False

        self.database = {}
        with open(self.database_path, 'w') as db_file
            logger.debug("Creating empty database at %s.", self.database_path)
            json.dump(self.database, db_file, indent=4)

        self.is_initialized = True
        return True

    def __load_database(self):
        logger.debug("Loading package database from %s", self.database_path)
        try:
            with open(self.database_path, 'r') as db_file:
                self.database = json.load(db_file)
            return True
        except FileNotFoundError:
            logger.debug("Couldn't find package database. %s not initialized!",
                         self.__class__.__name__)
            return False

    def __save_database(self):
        if self.is_initialized:
            logger.debug("Saving database at %s", self.database_path)
            with open(self.database_path, 'w') as db_file:
                json.dump(self.database, db_file, indent=4)
        else:
            logger.debug("Database not initialized, not saving it!")