#! /usr/bin/env python3

# system
import argparse
import logging
import os

# 3rdparty
from dialog import Dialog

# muninn imports
import muninn.common as common
import muninn.packages as packages
import muninn.builder as builder
import muninn.depresolver as depresolver


def install_system(pn_config_folder):
    common.setup_logging(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # Work with abosolute paths
    pn_config_folder = os.path.abspath(pn_config_folder)
    logger.debug("Switching to abspath: %s", pn_config_folder)

    # Search for packages
    pkg_paths = packages.search_packages(pn_config_folder)

    # Load pkgs
    pkgs = {name: packages.Package(name, path)
            for (name, path) in pkg_paths.items()}

    # Filter out invalid muninn pkgs
    pkgs = {name: pkg for (name, pkg) in pkgs.items() if pkg.valid}
    logger.debug("Valid muninn pkgs found: {}".format(pkgs.keys()))

    depends_graph = depresolver.build_graph(pkgs)
    install_order = depresolver.resolve_graph(depends_graph)

    # Filter out pkgs, which can not be installed due to unmet dependencies
    pkgs = {name: pkg for (name, pkg) in pkgs.items() if name in install_order}
    logger.debug("Pkgs with met dependencies: {}".format(pkgs.keys()))

    # Start GUI Part
    d = Dialog(dialog="dialog", autowidgetsize=True)

    # Collect Pkgs into choices
    choices = [(pkg.info["name"], pkg.info["desc"], False)
               for pkg in pkgs.values()]
    code, tags = d.checklist("Which programs do you want to install?",
                             choices=choices,
                             title="Muninn - Package / Config Installer",
                             )

    # Determine Muninn-internal dependencies of packages which need to be
    # satisfied
    required_dependencies = set()
    missing_dependencies = set()
    skipped_packages = []
    if code == d.OK:
        for idx, tag in enumerate(tags):
            # Recursively search and check what pkgs are required
            depends = set(
                depresolver.find_dependencies(tag, depends_graph))

            if depends.issubset(install_order):  # if depends can be satisfied
                # then collect those, which are not selected yet
                required_dependencies.update(depends.difference(set(tags)))
            else:
                missing_dependencies.update(depends.difference(install_order))
                skipped_packages.append(tag)
                logger.error("Dependencies ({}) can not be satisfied for {}"
                             .format(missing_dependencies, tag))

    depends_msg = "The following packages are required as dependencies,\
                   and are automatically selected for installation."

    logger.info(depends_msg + " {}".format(required_dependencies))
    if skipped_packages:
        logger.info("Following packages will be skipped: {}"
                    .format(skipped_packages))

    if required_dependencies:
        msg = "".join([depends_msg, "\n\n\n"] +
                      ["\t\t\t\t--> {}\n".format(d)
                       for d in required_dependencies] +
                      ["\n\nPress yes, to proceed with installation."])
        if d.yesno(msg) == d.OK:
            pass
        else:
            exit(0)

    tags = tags + list(required_dependencies)

    pkg_processed = []
    os.system('cls' if os.name == 'nt' else 'clear')
    for idx, tag in enumerate(tags):
        logger.info("Setting up: %s", tag)
        pkg_processed.append((tag, "In Progress"))
        retval = builder.install(pkgs[tag])
        pkg_processed[-1] = ((tag, "Success" if retval else "Failure"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    install_system("pkgs")
