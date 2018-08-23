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
import sys
from importlib import import_module

logger = logging.getLogger(__name__)


class InvalidMuninnPackage(Exception):
    pass


class MuninnPackageBlueprint():
    required = [
        # ("name", str),
    ]

    optional = [
        ("description", str),
        ("depends_arch", list, str),
        ("depends_muninn", list, str),
        ("conflicts", list, str),
        ("symlink_targets", list, tuple),
    ]

    install_execution_order = [
        "pre_install",
        "install",
        "post_install"
    ]

    uninstall_execution_order = [
        "uninstall"
    ]


def MuninnPackage(package_class):
    def check_for_attribute(cls, attribute_def, required=False):
        attribute_set = hasattr(cls, attribute_def[0])
        if required and not attribute_set:
            raise AssertionError(
                "Required attribute < {} > not set".format(attribute_def[0]))

        if attribute_set:
            assert type(getattr(cls, attribute_def[0])) == attribute_def[
                1], "Type of attribute {} should be {}, but is {}".format(
                attribute_def[0], attribute_def[1],
                type(getattr(cls, attribute_def[0])))

            if type(getattr(cls, attribute_def[0])) == list:
                assert all(isinstance(item, attribute_def[2]) for item in
                           getattr(cls, attribute_def[
                               0])), "Not all elements of list %s are of type %s" % (
                attribute_def[0], attribute_def[2])

    # now check if types are correct
    blueprint = MuninnPackageBlueprint()

    try:
        for required in blueprint.required:
            check_for_attribute(package_class, required, required=True)

        for optional in blueprint.optional:
            check_for_attribute(package_class, optional, required=False)

        # pass all asserts, then attribute for valid package
        package_class.valid = True
    except AssertionError as e:
        logger.debug(e)
        # didnt all asserts, add attribute for valid package
        package_class.valid = False
        raise InvalidMuninnPackage(e)

    return package_class


def load_package(path, name):
    # Temporally add the pkg folder to sys.path, and remove it later. Since
    # all modules share the same name 'muninn_pkg', we will not be able to
    # load the next module correctly otherwise.
    logger.debug("Loading module at {}".format(str(path)))
    sys.path.append(path)
    module = import_module(name)
    return getattr(module, "Package")
