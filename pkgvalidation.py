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

# import muninn.packages as packages

common.setup_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class InvalidMuninnPackage(Exception):
    pass


class MuninnPackageBlueprint():
    required = [
        ("name", str),
        ("description", str),
        ("version", str),
    ]

    optional = [
        ("depends_arch", list, str),
        ("depends_muninn", list, str),
        ("conflicts", list, str),
        ("symlink_targets", list, tuple),
    ]


def MuninnPackage(package_class):
    # now check if types are correct
    blueprint = MuninnPackageBlueprint()

    try:
        for required in blueprint.required:
            assert hasattr(package_class, required[0])
            assert type(getattr(package_class, required[0])) == required[
                1], "Type of .%s should be %s, but is %s" % (required[0],
                                                             required[1], type(
                getattr(package_class, required[0])))

            if type(getattr(package_class, required[0])) == list:
                assert all(isinstance(item, required[2]) for item in
                           getattr(package_class, required[
                               0])), "Not all elements of list %s are of required type %s" % (
                    required[0], required[2])

        for optional in blueprint.optional:
            if hasattr(package_class, optional[0]):
                assert type(getattr(package_class, optional[0])) == optional[
                    1], "Type of optional .%s should be %s, but is %s" % (
                    optional[0], optional[1],
                    type(getattr(package_class, optional[0])))

                if type(getattr(package_class, optional[0])) == list:
                    assert all(isinstance(item, optional[2]) for item in
                               getattr(package_class, optional[
                                   0])), "Not all elements of list %s are of required type %s" % (
                        optional[0], optional[2])

        # pass all asserts, add attribute for valid package
        package_class.__valid_muninn_pkg = True
    except AssertionError as e:
        logger.debug(e)
        # didnt all asserts, add attribute for valid package
        package_class.__valid_muninn_pkg = False
        raise InvalidMuninnPackage

    return package_class


@MuninnPackage
class ZSH():
    name = "zsh"
    description = "Install ZSH, oh-my-zsh, and place symlinks to config files."
    version = "0.0.1"
    depends_arch = [
        "zsh",
        "powerline",
        "powerline-fonts"
    ]
    depends_muninn = ["system_setup"]
    conflicts = []
    symlink_targets = [
        (".zsh", "~/"),
    ]


def main():
    import pkgutil
    import inspect
    import repository
    for (module_loader, name, ispkg) in pkgutil.iter_modules(repository.__path__):

        loader, path = module_loader.find_loader(name)
        a = loader.load_module()
        clsmembers = inspect.getmembers(a, inspect.isclass)
        print(clsmembers)
        # try:
            #     pkg = ZSH()
            #     print(getattr(pkg, '__valid_muninn_pkg'))
            #     # validate_package(ZSH)
            #     # print(inspect.getsource(packages.MuninnPackage))
            # except TypeError as e:
            #     print(e)


if __name__ == '__main__':
    main()
