import logging
logger = logging.getLogger(__name__)

pkg = {
    "name": "terminator",
    "desc": "Terminator Configuration",
    "ver": 0.1,
    "depends": {
        "arch": [
            "terminator"
        ],
        "muninn": [
        ]
    },
    "conflicts": [],

    "install_path": "~/.config/terminator",
    "targets": [
        "config",
        "plugins",
    ]
}
