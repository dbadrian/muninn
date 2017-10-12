import logging
import os
import sys
from importlib import import_module

import muninn.common as common

logger = logging.getLogger(__name__)


class Package(object):
    """
    Class definition for Muninn type package including some minor validation of
    the package instructions.
    """

    def __init__(self, pkg_name, path_to_pkg):
        self.path = path_to_pkg

        # Temporally add the pkg folder to sys.path, and remove it later. Since
        # all modules share the same name 'muninn_pkg', we will not be able to
        # load the next module correctly otherwise.
        sys.path.append(path_to_pkg)
        logger.debug("Loading pkg: %s", pkg_name + "_muninn")
        pkg = import_module(pkg_name + "_muninn")

        if self.__validate_pkg(pkg, pkg_name):
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
        else:
            self.valid = False

    def backup(self, pkg_dir, target_dir, backup_folder):
        pass

    def install(self, pkg_dir, target_dir):
        pass

    def post_install(self, pkg_dir, target_dir):
        pass

    def clean(self, pkg_dir, target_dir):
        pass

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