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

import logging

import muninn.common as common

import muninn.repository as repo

common.setup_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)



def main():
    rp = repo.Repository("/tmp/muninn_repo")
    # rp.initialize_repository()
    # rp.start_tracking_package("zsh")
    # rp.update_package("zsh")

    # print(rp.get_package_revisions("zsh"))
    # print(rp.current_package_revision("zsh"))

    rp.list_untracked_packages()

if __name__ == '__main__':
    main()
