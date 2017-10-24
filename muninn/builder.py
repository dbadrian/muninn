import os
import glob
import logging
import subprocess
import datetime
import shutil

import muninn.common as common


logger = logging.getLogger(__name__)


def install(pkg):

    logger.debug(pkg)

    # Ensure User-Input Makes sense
    target_dir = os.path.expanduser(pkg.info["install_path"])
    bak_date = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    bak_dir = os.path.join(pkg.path, "_muninn_bak", bak_date)
    # Create backup folder
    logger.debug("Creating backup folder for %s", pkg.path)
    common.mkdir_p(bak_dir)

    try:
        logger.debug("running installer::%s::pkg_backup_func", pkg.path)
        if "backup" in dir(pkg):
            pkg.backup(pkg.path, target_dir, bak_dir)
    except Exception as e:
        logger.exception("Install Step pkg.backup failed.")
        return False

    try:
        logger.debug("running installer::%s::core_backup_func", pkg.path)
        if pkg.info["targets"]:
            backup_targets(pkg.info["targets"], pkg.path,
                           target_dir, bak_dir)
    except Exception as e:
        logger.exception("Install Step backup_targets failed.")
        return False

    try:
        install_arch_dependencies(pkg.info["depends"]["arch"])
    except Exception as e:
        logger.exception("Installing arch:dependencies failed.")
        return False

    try:
        logger.debug("running installer::%s::pkg_install_func", pkg.path)
        if "install" in dir(pkg):
            pkg.install(pkg.path, target_dir)
    except Exception as e:
        logger.exception("Install Step pkg.install failed.")
        return False

    try:
        logger.debug("running installer::%s::core_link_targets", pkg.path)
        if pkg.info["targets"]:
            link_targets(pkg.info["targets"], pkg.path,
                         target_dir)
    except Exception as e:
        logger.exception("Install Step link_targets failed.")
        return False

    try:
        if "post_install" in dir(pkg):
            pkg.post_install(pkg.path, target_dir)
    except Exception as e:
        logger.exception("Install Step pkg.post_install failed.")
        return False

    try:
        if "clean" in dir(pkg):
            pkg.clean(pkg.path, target_dir)
    except Exception as e:
        logger.exception("Install Step pkg.clean failed.")
        return False

    try:
        clean(bak_dir)
    except Exception as e:
        logger.exception("Install Step pkg.clean failed.")
        return False

    return True


def backup_targets(targets, module_dir, target_dir, bak_dir):
    if not os.path.exists(target_dir):
        logger.error("\"%s\" does not exist. Nothing to backup.",
                     target_dir)
        return None
    else:
        # Since users can use * wildcard, we need to figure out what files exist
        # in the pkg folder, and only backup those or unwanted side-effects
        # could happen.
        # Collect file names
        fn_queue = []
        for target in targets:
            path_origin = os.path.join(module_dir, target)
            # process unix style wildcards
            for file in glob.glob(path_origin):
                fn_queue.append(file.rsplit("/", 1)[1])

        for target in fn_queue:
            file = os.path.join(target_dir, target)
            # process unix style wildcards
            if not os.path.exists(file):
                logger.error("\"%s\" does not exist. Nothing to backup.", file)
            else:
                if not os.path.islink(file):
                    shutil.move(file, bak_dir)


def install_arch_dependencies(dependencies):
    # Check what is already installed
    depends_list = [depend for depend in dependencies if
                    subprocess.run(["pacaur", "-Qi", depend],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL).returncode]

    # Only run if list is not empty
    if depends_list:
        subprocess.run(["pacaur", "-S"] + depends_list, stdout=subprocess.PIPE)


def link_targets(targets, module_dir, target_dir):
    if not os.path.exists(target_dir):
        logger.error("\"%s\" does not exist. Can't create symlinks.",
                     target_dir)
        return None
    else:
        for target in targets:
            path_origin = os.path.join(module_dir, target)
            # process unix style wildcards
            for file in glob.glob(path_origin):
                dst = os.path.join(target_dir, file.rsplit("/", 1)[1])
                try:
                    if os.path.islink(dst):
                        common.force_symlink(file, dst)
                    else:
                        os.symlink(file, dst)
                except FileExistsError:
                    logger.error(
                        "A file still/already exists at: %s", dst)


def clean(bak_dir):
    try:
        os.rmdir(bak_dir)
        logger.debug("Deleted Backup folder %s, because its empty.", bak_dir)
    except OSError as ex:
        logger.debug("Backup folder not empty after backup, \
                      no garbage cleaning needed.")
