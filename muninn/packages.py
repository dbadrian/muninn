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
import os
import re
import sys
from importlib import import_module

import muninn.common as common

logger = logging.getLogger(__name__)


class Package(object):
    """
    Class definition for Muninn type package including some minor validation of
    the package instructions.
    """

    def __init__(self, pkg_name, path_to_pkg, n_commits=1):
        self.path = path_to_pkg
        self.pkg_name = pkg_name

        self.commits = common.get_commits(self.path, n_commits)
        # collect all the version numbers by regex from the file
        self.version2hash = {
            self.__get_version_number_for_commit(commit): commit
            for commit in self.commits}
        # delete key None if present, as its a results from old commit references
        if None in self.version2hash:
            self.version2hash.pop(None, None)

        self.versions = list(self.version2hash.keys())
        self.versions.sort(reverse=True)

    def load_module(self, version=None, hash=None):
        logger.debug("Starting loading routine of pkg %s", self.pkg_name)
        try:
            assert version or hash, "Neither version or hash given!"
            assert not version and hash or version and not hash, "Only version or hash can be defined!"
        except AssertionError as e:
            logger.debug(e)
            return False

        if version == "latest" or hash == "latest":
            # If the testing param was set, we use the current state of the folder
            # which might not be tracked as commit in the repository. Allows for testing of new packages.
            logger.debug("Loading package at current state!")
            self.__load_module(self.path)
        else:
            raise NotImplementedError
            # TODO: Instead of symlinking, copy files!
            # TODO: Only status=latest installed files are being tracked in the repo
            # if version:
            #     # Will be the correct hash or None if this version doesn't exist
            #     logger.debug("Loading package at version=%s", version)
            #     try:
            #         hash = self.version2hash[version]
            #     except KeyError:
            #         logger.debug("Version not found!")
            #         return False
            # if hash in self.commits:
            #     # checkout the folder into a temporary directory given the
            #     logger.debug("Loading package at hash=%s", hash)
            #     with common.tempdir() as tmp_dir_path:
            #         common.checkout_path_at_commit(self.path, hash,
            #                                        tmp_dir_path)
            #         self.__load_module(tmp_dir_path)
            # else:
            #     logger.debug("Hash not found!")
            #     return False

    def backup(self, pkg_dir, target_dir, backup_folder):
        pass

    def install(self, pkg_dir, target_dir):
        pass

    def post_install(self, pkg_dir, target_dir):
        pass

    def clean(self, pkg_dir, target_dir):
        pass

    def __load_module(self, path):
        # Temporally add the pkg folder to sys.path, and remove it later. Since
        # all modules share the same name 'muninn_pkg', we will not be able to
        # load the next module correctly otherwise.
        sys.path.append(path)
        pkg = import_module(self.pkg_name + "_muninn")

        if self.__validate_pkg(pkg, self.pkg_name):
            self.valid = True
            self.info = pkg.pkg

            if "backup" in dir(pkg):
                logger.debug("Added PKG Backup Function")
                self.backup = pkg.backup

            if "install" in dir(pkg):
                logger.debug("Added PKG Install Function")
                self.install = pkg.install

            if "post_install" in dir(pkg):
                logger.debug("Added PKG Post-Install Function")
                self.post_install = pkg.post_install

            if "clean" in dir(pkg):
                logger.debug("Added PKG Clean Function")
                self.clean = pkg.clean

            return True
        else:
            logger.debug("Package %s not valid, skipping loading!",
                         self.pkg_name)
            self.valid = False
            return False

    def __validate_pkg(self, pkg, pkg_name):
        # Check if the user correctly edited the pkg
        if not pkg_name == pkg.pkg["name"]:
            logger.error("Invalid Muninn PKG: Name mismatch.")
            return False

        if "pkg" not in dir(pkg):
            logger.error("Invalid Muninn PKG: No pkg-info defined.")
            return False

        # Check if package does nothing
        if not pkg.pkg["depends"]["arch"] and \
                not pkg.pkg["depends"]["muninn"] and \
                not pkg.pkg["targets"] and \
                        "install" not in dir(pkg) and \
                        "post_install" not in dir(pkg):
            logger.error("Invalid Muninn PKG: No actions defined.")
            return False

        return True

    def __get_version_number_for_commit(self, commit):
        muninn_pkg_file = os.path.join(self.path, self.pkg_name + "_muninn.py")
        content = common.get_file_at_commit(muninn_pkg_file, commit)
        return self.__extract_version_number(content)

    def extract_version_number(self):
        path = os.path.join(self.path, self.pkg_name + "_muninn.py")

        with open(path, 'r') as pkg_data:
            pkg_text = pkg_data.read()
            return self.__extract_version_number(pkg_text)

    def bump_version_number(self, major=False, minor=False, patch=False):
        path = os.path.join(self.path, self.pkg_name + "_muninn.py")
        with open(path, 'r') as pkg_data:
            pkg_text = pkg_data.read()
            current_version = self.__extract_version_number(pkg_text)
            bumped_version = common.bump_version(current_version, major, minor,
                                                 patch)

            pkg_text = re.sub(r'("version":\s*")([\d.]+)',
                              "\\g<1>" + bumped_version, pkg_text)

        with open(path, 'w') as pkg_data:
            pkg_data.write(pkg_text)

    def __extract_version_number(self, file_content):
        res = re.search('"version":\s*"([\d.]+)"', file_content)
        if res:
            return res.group(1)
        else:
            return None

    def __load_hash(self, file_path, hash, output_path):
        pass


def search_packages(pkgs_path):
    """
    @brief      Searches a folder for Muninn-packages (containg
                name.munnin.py file)

    @param      pkgs_path  Path to search folder

    @return     List of Munnin-packges
    """
    if not os.path.exists(pkgs_path):
        logger.error("%s does not exist. Search terminated.", pkgs_path)
        return None
    else:
        logger.info("Searching packages in: %s", pkgs_path)

        # just aggregate all potential pkgs
        pkg_candidates = common.get_immediate_subdirectories(pkgs_path)
        logger.debug("Package Candidates %s", pkg_candidates)

        # check if they contain a muninn pkg declaration (no validation!)
        packages = {pkg_candidate: os.path.join(pkgs_path, pkg_candidate)
                    for pkg_candidate in pkg_candidates if os.path.exists(
            os.path.join(pkgs_path, pkg_candidate,
                         pkg_candidate + "_muninn.py"))}

        logger.info("Found %i packages: %s", len(packages), packages)
        return packages
