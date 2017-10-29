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

import argparse
import logging
import os
import sys
from itertools import groupby

import muninn.common as common
from muninn.package_manager import PackageManager

common.setup_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    import coloredlogs

    coloredlogs.install(level='ERROR')
except:
    pass


def split_pkg_list_by_version(pkg_list, default_key='latest'):
    """
    Takes a list of names with and with out '=<version>' attached, and splits
    accordingly into tuples. If no version string is given, the default key word
    is used.
    """
    return [(x[0], x[1] if len(x) == 2 else default_key) for x in
            (pkg.split("=") for pkg in pkg_list)]


class Muninn(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            usage='muninn <command> [<args>]\n\n'
                  'Available muninn commands:\n'
                  '   install     Install (list of) package(s) (=version for specific version)\n'
                  '   remove      Remove installed package(s) and restore local backups\n'
                  '   backup      Commits and pushes current state of muninn and repository\n'
                  '   list        List all available packages\n'
        )
        parser.add_argument('command', help='Command to run')

        # check if first arg exists as function
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def install(self):
        parser = argparse.ArgumentParser(
            description='Install (list of) package(s) (=version for specific '
                        'version)')
        parser.add_argument('-f', '--force', action='store_true',
                            help="Force re-installation if package(s) is already "
                                 "installed.")
        parser.add_argument('-p', '--packages', nargs='+', required=True,
                            help='(List of) desired package(s)')
        parser.add_argument('-r', '--repository', type=str, required=False,
                            default='./repository',
                            help='Non-default location of local repository.')
        parser.add_argument('--dry_run', action='store_true', required=False,
                            help="Prints detailed output of changes, but no "
                                 "actual modification of the system occurs!")
        args = parser.parse_args(sys.argv[2:])
        logger.debug("Called with args: %s", args)
        exit(self.__install(args))

    def remove(self):
        raise NotImplementedError

    def backup(self):
        parser = argparse.ArgumentParser(
            description='Backup packages by creating a new commit and pushing.')
        parser.add_argument('-m', '--message', type=str, required=False,
                            help='Message for this commit.')
        parser.add_argument('-d', '--detailed', action='store_true',
                            required=False, help="Extended informations.")
        parser.add_argument('-r', '--repository', type=str, required=False,
                            default='repository',
                            help='Non-default location of local repository.')

        args = parser.parse_args(sys.argv[2:])
        exit(self.__backup(args))

    def list(self):
        parser = argparse.ArgumentParser(
            description='List available packages in repository')
        # prefixing the argument with -- means it's optional
        parser.add_argument('-d', '--detailed', action='store_true',
                            required=False, help="Extended informations.")
        parser.add_argument('-p', '--packages', nargs='+', required=False,
                            help='List only specified packages.')
        parser.add_argument('-s', '--search', nargs='+', required=False,
                            help='Search for terms and list matching packages.')
        parser.add_argument('-i', '--installed', action='store_true',
                            required=False, help="Only looks within the set "
                                                 "of installed packages.")
        parser.add_argument('-r', '--repository', type=str, required=False,
                            default='./repository',
                            help='Non-default location of repository.')
        args = parser.parse_args(sys.argv[2:])
        exit(self.__list(args))

    def __install(self, args):
        # parse packages into pkg and desired version if given
        desired_packages = split_pkg_list_by_version(args.packages)
        pm = PackageManager(args.repository)

        print(":: Resolving Dependencies")
        install_order, removed_pkgs = pm.load_and_resolve_dependencies(
            desired_packages)

        if removed_pkgs:
            msg = "Following packages removed due to unresolved dependencies:\n" \
                  + ''.join(
                ["   " + str(idx) + ". " + pkg_name + "\n" for idx, pkg_name in
                 enumerate(removed_pkgs)]) + "\n\n"
            print(msg)
            logger.info(
                "Following packages (and dependencies) will not be installed, "
                "because of unresolved dependencies: %s", removed_pkgs)

        not_installed = []
        incorrect_version = []
        if not args.force:
            not_installed, incorrect_version = pm.filter_install_order(
                install_order)
            logger.debug("Incorrect Version %s", incorrect_version)

            install_order = not_installed + incorrect_version

        # if nothing to install, do an early exit
        if not install_order:
            print(" ==> Nothing to install, bye!")
            exit(0)

        print(":: Installing packages" + " (dry-run)" if args.dry_run else "")
        if not_installed:
            msg = "".join(
                ["   " + str(idx) + ". " + name + " ==> " + version + "\n" for
                 idx, (name, version) in enumerate(not_installed)]) + "\n"
            print(msg)

        if incorrect_version:
            msg = "".join(["   {}. {} ==> {} (from {})\n".format(str(idx), name,
                                                                 version,
                                                                 pm.installed_package_version(
                                                                     name)) for
                           idx, (name, version) in
                           enumerate(incorrect_version)])
            print(msg)

        if not args.dry_run and common.yes_or_no(
                "Please confirm the changes above to continue."):
            return pm.install_packages(install_order)

    def __backup(self, args):
        pm = PackageManager(args.repository)

        # print summary of all modified files and changes according to current
        changed = common.get_changed_files(args.repository)
        changed_g = {k: list(g) for k, g in
                     groupby(changed, lambda s: s.split(os.sep)[0])}
        untracked = common.get_untracked_files(args.repository)
        untracked_g = {k: list(g) for k, g in
                       groupby(untracked, lambda s: s.split(os.sep)[0])}

        changed_pkgs = set(
            [path.split(os.sep)[0] for path in changed + untracked])

        print("\nPackages staged for commit:\n   {}".format(
            "\n   ".join(changed_pkgs)))

        if args.detailed:
            print("\nFiles modified / deleted since last commit:")
            for path in changed:
                print('\tmodified:', path)

            print("\nFiles not tracked yet:")
            for path in untracked:
                print('\tmodified:', path)

        # generate text with grouping by packages and list modified and untracked
        # files. everything without a hashtag will be added to comming up commit.
        pkg_msg = "############################################################\n" \
                  "#### {}\n" \
                  "############################################################\n" \
                  "# modified / deleted files:\n" \
                  "{}\n" \
                  "# untracked files:\n" \
                  "{}\n\n"

        msg = "############################################################\n" \
              "# Please confirm the changes which will be recorded in the \n" \
              "# commit. Lines (= files) starting with '#' will be ignored.\n" \
              "############################################################\n\n"

        for pkg in changed_pkgs:
            s_changed = "\n".join(
                changed_g[pkg]) if pkg in changed_g else "# <no changes> "
            s_untracked = "\n".join(
                untracked_g[pkg]) if pkg in untracked_g else "# <no changes>"

            msg += pkg_msg.format(pkg, s_changed, s_untracked)

        ret = common.message_from_sys_editor(msg)
        files_to_stage = common.get_non_comment_lines(ret)

        print("\nFollowing files have been selected for staging:\n")
        for file in files_to_stage:
            print("    ", file)

        print("\nIncrementing package versions as following:")
        for pkg in changed_pkgs:
            print("    ", pkg, ": old version ==> new version")

        if not common.yes_or_no("\nCommit the changes above?"):
            exit(0)

        # do a version bump and remember changes

        # # git add those files
        # common.stage_files(args.repository, files_to_stage)
        #
        # # a git commit # get message of user via the actual git commit tool if necessary
        # msg = args.message
        # if not msg:
        #     msg = "\n\n" \
        #           "############################################################\n" \
        #           "# Please shortly summarize all the changes made to the repo! \n" \
        #           "# Lines (= files) starting with '#' will be ignored.\n" \
        #           "# First line is short summary, following lines are extended.\n" \
        #           "############################################################\n\n"
        #
        #     msg = common.message_from_sys_editor(msg)
        #
        # common.commit(args.repository, message=msg)

        # print("\nPushing new commit to remote repository.")
        # common.push(args.repository)

    def __list(self, args):
        raise NotImplementedError


if __name__ == '__main__':
    Muninn()
