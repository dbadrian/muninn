#!/bin/zsh
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

# Check if commit message has been set
if [ $# -eq 0 ]
  then
    echo "No commit message supplied! Exiting..."
    exit
fi

#DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DIR="$( cd "$(dirname "$0")" ; pwd -P )"
echo $DIR
cd ${DIR}

# Create latest conda env file
conda env export -n muninn | grep -v "^prefix: "> ${DIR}/muninn_conda_env

# Auto generate new readme
# TODO
source activate muninn
python autogen_readme.py

# Make new git commit
git commit -am "$1"

# And push
git push
