import logging
import os

import muninn.common as common

logger = logging.getLogger(__name__)

pkg = {
    "name": "tensorflow",
    "desc": "Tensorflow compiled from source",
    "ver": 0.1,
    "depends": {
        "arch": [
            "cuda",
            "cudnn",
            "bazel"
        ],
        "muninn": [
            # "system_setup"
        ]
    },
    "conflicts": [],

    "install_path": "~/",
    "targets": [
    ]
}


def backup(pkg_dir, target_dir, backup_folder):
    """
    If anything needs to be done additionally to back-upping the
    files/folders defined in backup
    """
    pass


def install(pkg_dir, target_dir):
    """
    If anything needs to be installed/configured before placing symlinks
    on targets, use this function.
    """
    with common.tempdir() as tmpdir:
        logger.debug("Calling install script")
        common.run_linux_cmd("zsh " + os.path.join(common.get_current_module_folder(), 'tensorflow_setup.zsh') + " " + tmpdir)


def post_install(pkg_dir, target_dir):
    """
    If anything needs to done after placing symlinks
    on targets, use this function.
    """
    pass

def clean(pkg_dir, target_dir):
    """
    If anything needs to be done manually if something fails,
    please specify here.
    """
    pass
