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

import muninn.packages as packages

common.setup_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)



def main():
    import pkgutil
    import inspect
    import repository
    for (module_loader, name, ispkg) in pkgutil.iter_modules(repository.__path__):

        loader, path = module_loader.find_loader(name)
        try:
            a = loader.load_module()
            clsmembers = inspect.getmembers(a, inspect.isclass)
            print(clsmembers[0][1]().description)
        except packages.InvalidMuninnPackage as e:
            print(e)
        # try:
            #     pkg = ZSH()
            #     print(getattr(pkg, '__valid_muninn_pkg'))
            #     # validate_package(ZSH)
            #     # print(inspect.getsource(packages.MuninnPackage))
            # except TypeError as e:
            #     print(e)


if __name__ == '__main__':
    main()
