import logging
logger = logging.getLogger(__name__)

pkg = {
    "name": "archpackages",
    "desc": "Arch Linux Packages Installer",
    "ver": 0.1,
    "depends": {
        "arch": [
            # Laptop Energy Management
            "acpi",
            "acpid",
            "powertop",

            # Drivers
            "nvidia",

            # System Utils
            "alsa-tools",
            "alsa-utils",
            "cups",
            "dhcpcd",
            "dialog",
            "diffutils",
            "e2fsprogs",
            "efibootmgr",
            "docker",
            "downgrade",
            "exfat-utils",
            "fakeroot",
            "gparted",
            "ibus-anthy",
            "ibus-qt",
            "virt-manager",
            "wget",
            "wpa_supplicant",
            "xfsprogs",
            "rsync",
            "screen",
            "sshfs",
            "sysfsutils",
            "unrar",
            "usbutils",
            "util-linux",
            "xorg-server",
            "xorg-server-utils",
            "xorg-xinit",
            "inetutils",
            "intel-ucode",
            "iproute2",
            "iputils",
            "networkmanager-openvpn",
            "nmap",
            "nvidia-docker",
            "nvidia-settings",
            # Encryption Tools
            "cryptsetup",
            "dislocker",

            # Important Libs
            # "ceres-solver",
            # "suitesparse",
            "ffmpegthumbs",
            "eigen",
            "adobe-base-14-fonts",
            "flashplugin",
            "adobe-source-han-sans-jp-fonts",
            "fuse3",
            "ntfs-3g",
            "hplip",
            "jdk8-openjdk",
            "jfsutils",
            "lib32-libpulse",
            "lib32-nvidia-utils",
            "lib32-openal",
            "powerline",
            "powerline-fonts",
            "lib32-opencl-nvidia",
            "p7zip",
            "opencl-headers",
            "opencl-nvidia",
            "samba",
            "sudo",
            "openmp",
            "openssh",
            "openvpn",
            "reiserfsprogs",

            # Useful Stuff
            "aria2",
            "filezilla",
            "genius",
            "htop-solarized",
            "jdownloader2",
            "terminator",
            "xclip",

            # Coding and Scripting
            "nano",
            "sublime-text-dev",
            "kdiff3",
            "git",
            "gitg",
            "arduino",
            "cuda",
            "cudnn",
            "cudnn6",
            "graphviz",

            # text editing and Tex
            "hunspell-de",
            "hunspell-en",
            "otf-ipafont",
            "libreoffice-fresh",
            "libreoffice-fresh-de",
            "texinfo",
            "texlive-most",
            "texlive-lang",
            "texstudio",
            "ttf-google-fonts-git",
            "ttf-hanazono",
            "ttf-inconsolata-g",
            "ttf-koruri",
            "ttf-liberation",
            "ttf-monapo",
            "ttf-mplus",
            "ttf-ms-fonts",
            "ttf-sazanami",
            "ttf-vlgothic",

            # Management tools
            "gnucash",

            # Everyday Tools
            "chromium",
            "acroread",
            "anki20-bin",
            "calibre",
            "irssi",
            "mplayer",
            "vlc",
            "wine",
            "steam",
            "skypeforlinux-bin",
            "redshift-gtk-git",
            "okular",
            "zotero",

            # photoediting
            "darktable-git",
            "gimp",
            "gwenview",
            "photoqt",


            # backup
            "restic",
        ],
        "muninn": [
            "system_setup"
        ]
    },
    "conflicts": [],
    "install_path": "~/",
    "targets": [
    ]
}