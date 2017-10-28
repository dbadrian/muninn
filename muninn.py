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
import sys

import muninn.common as common
from muninn.package_manager import PackageManager

common.setup_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    import coloredlogs

    coloredlogs.install(level='DEBUG')
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
        # prefixing the argument with -- means it's optional
        parser.add_argument('-f', '--force', action='store_true',
                            help="Force re-installation if package is already "
                                 "installed.")
        parser.add_argument('-p', '--packages', nargs='+', required=True,
                            help='(List of) desired package(s)')
        parser.add_argument('-r', '--repository', type=str, required=False,
                            default='./repository',
                            help='Non-default location of repository.')
        parser.add_argument('--dry_run', action='store_true', required=False,
                            help="Determined packages and depencies, but will "
                                 "not modify the system.")
        args = parser.parse_args(sys.argv[2:])
        logger.debug("Called with args: %s", args)
        exit(self.__install(args))

    def backup(self):
        parser = argparse.ArgumentParser(
            description='Backup something?')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('repository')
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

        return pm.install_packages(desired_packages, dry_run=args.dry_run,
                                   force_reinstall=args.force)

    def __backup(self, args):
        raise NotImplementedError

    def __list(self, args):
        raise NotImplementedError


if __name__ == '__main__':
    Muninn()
