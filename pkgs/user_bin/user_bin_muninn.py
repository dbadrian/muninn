import logging
logger = logging.getLogger(__name__)

pkg = {
    "name": "user_bin",
    "desc": "Sync User Bin scripts",
    "ver": 0.1,
    "depends": {
        "arch": [
        ],
        "muninn": [
        ]
    },
    "conflicts": [],

    "install_path": "~/bin",
    "targets": [
        "tkill",
        "tsuspend",
        "moodle_dump",
        "start_restic_server"
    ]
}
