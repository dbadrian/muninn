#!/usr/bin/bash

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


########################################################
##################### CONFIG PARAMTERS #################
########################################################
EMAIL="dawidh.adrian@googlemail.com"

MUNINN_INSTALL_FOLDER=$HOME/git/muninn

GITHUB_USERNAME="dbadrian"
GITHUB_KEY_NAME="laptop"

CONDA_VERSION="5.2.0"

############## DO NOT MODIFY BELOW THIS LINE ###########
# This does not resolve from a symlink location
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MUNINN_REPO="git@github.com:dbadrian/muninn.git"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

########################################################
##################### Function Def #####################
########################################################

yes_or_no_run() {
    echo -e ${1}
    select yn in "Yes" "No"; do
    case $yn in
        Yes ) ${@:2}; break;;
        No ) break;;
    esac
    done
}

create_ssh_key() {
    sudo pacman -S openssh
    ssh-keygen -t rsa -b 4096 -C "${1}"
}

setup_sshkey_github() {
    echo -e "Publishing key=${2} to github user account ${1}"
    curl -u ${1} --data '{"title":"'${2}'","key":"'"$(cat ~/.ssh/id_rsa.pub)"'"}' https://api.github.com/user/keys
}

install_conda() {
    wget https://repo.anaconda.com/archive/Anaconda3-${1}-Linux-x86_64.sh -P /tmp
    bash /tmp/Anaconda3-${1}-Linux-x86_64.sh -b -p $HOME/anaconda3
    export PATH="$HOME/anaconda3/bin:$PATH"
}

setup_muninn_conda_env() {
    # create conda-environment from file
    conda env create -f ${1}/muninn_conda_env
}

setup_muninn() {
    mkdir -p "$2"
    git clone $1 $2
}

########################################################
##################### Main Routine #####################
########################################################

yes_or_no_run "${RED}Generate new SSH Key?${NC}" create_ssh_key ${EMAIL}
yes_or_no_run "${RED}Publish main SSH Key to Github?${NC}" setup_sshkey_github ${GITHUB_USERNAME} ${GITHUB_KEY_NAME}

yes_or_no_run "${RED}Install anaconda3?${NC}" install_conda ${CONDA_VERSION}

yes_or_no_run "${RED}Setup/Clone Muninn?${NC}" setup_muninn $MUNINN_REPO $MUNINN_INSTALL_FOLDER
yes_or_no_run "${RED}Setup Muninn conda env?${NC}" setup_muninn_conda_env $MUNINN_INSTALL_FOLDER

echo -e "${GREEN}Done. System Bootstrapped!${NC}"