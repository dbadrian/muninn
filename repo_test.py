#! /usr/bin/env python3
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

# system
import argparse
import logging
import os

# muninn imports
import muninn.common as common
import muninn.package_manager as database


def main():
    common.setup_logging(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    db = database.PackageManager("repository")
    db.initialize_new_database()
    for name, pkg in db.pkgs.items():
        for version in pkg.versions:
            pkg.load_module(version=version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main()
