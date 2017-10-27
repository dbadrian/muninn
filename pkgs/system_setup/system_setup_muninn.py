import logging
logger = logging.getLogger(__name__)

pkg = {
    "name": "system_setup",
    "desc": "ArchLinux System-Configuration",
    "ver": "0.0.1",
    "depends": {
        "arch": [
        ],
        "muninn": [
        ]
    },
    "conflicts": [],

    "install_path": "/dev/null",
    "targets": [
    ]
}


def install(pkg_dir, target_dir):
    """
    If anything needs to be installed/configured before placing symlinks
    on targets, use this function.
    """

    # Install oh-my-zsh by curl
    import subprocess
    import os
    scripts = os.listdir(os.path.join(pkg_dir, "scripts"))
    for script in scripts:
        logger.info("Running: %s", script)
        cmd = os.path.join(pkg_dir, "scripts", script)
        subprocess.run([cmd])
