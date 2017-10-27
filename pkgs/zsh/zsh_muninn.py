import logging
logger = logging.getLogger(__name__)

pkg = {
    "name": "zsh",
    "desc": "ZSH Config Installer",
    "ver": "0.0.1",
    "depends": {
        "arch": [
            "zsh",
            "powerline",
            "powerline-fonts"
        ],
        "muninn": [
        ]
    },
    "conflicts": [],

    "install_path": "~/",
    "targets": [
        ".zprofile",
        ".zsh*",
    ]
}


def install(pkg_dir, target_dir):
    """
    If anything needs to be installed/configured before placing symlinks
    on targets, use this function.
    """

    # Install oh-my-zsh by curl
    cmd = """sh -c \"$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)\""""
    import subprocess
    subprocess.run(cmd, shell=True)


def post_install(pkg_dir, target_dir):
    """
    If anything needs to done after placing symlinks
    on targets, use this function.
    """
    logger.info("Please source ~/.zshrc or reload your terminal!")

    # Activate Shell
    # if subprocess.run("ps -p $$ -ocomm=".split()) #call doesnt work
    import subprocess
    subprocess.run("chsh -s /bin/zsh".split())
