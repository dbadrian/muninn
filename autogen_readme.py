#! /usr/bin/env python3
import datetime
import logging
import os

import muninn.common as common
import muninn.package as packages
import muninn.text

common.setup_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def make_pkg_string(pkg):
# [(pkg.info["name"], pkg.info["desc"], False)
#                for pkg in pkgs.values()]
    pkg_deps = " ".join(pkg.info["depends"]["muninn"]) if pkg.info["depends"]["muninn"] else "*None*"
    base_pkg_string = str(pkg.info["name"]) + " | " \
                     + str(pkg.info["ver"])  +" | " \
                     + str(pkg.info["desc"]) + " | " \
                     + pkg_deps + "\n"
    return base_pkg_string


def generate_supported_pkgs_string():
    pn_config_folder = os.path.abspath("pkgs")
    logger.debug("Switching to abspath: %s", pn_config_folder)

    # Search for packages
    pkg_paths = packages.search_packages(pn_config_folder)

    # Load pkgs
    pkgs = {name: packages.Package(name, path)
            for (name, path) in pkg_paths.items()}

    # Filter out invalid muninn pkgs
    pkgs = {name: pkg for (name, pkg) in pkgs.items() if pkg.valid}
    logger.debug("Valid muninn pkgs found: {}".format(pkgs.keys()))

    table_str = "Package Name | Version | Description | Dependencies Muninn\n--- | --- | --- | --- \n"
    for (name, pkg) in pkgs.items():
        table_str += make_pkg_string(pkg)

    return table_str

def main():
    pkg_table = generate_supported_pkgs_string()


    with open("templates/muninn_readme.tpl", 'r') as f_sample:
        readme_txt = f_sample.read()
        readme_txt = muninn.text.replace_tags(readme_txt, "SUPPORTED_PACKAGES_PLACEHOLDER", pkg_table)

    with open("muninn_conda_env", 'r') as f_sample:
        readme_txt = muninn.text.replace_tags(readme_txt, "ANACONDA_REQUIREMENTS_FILE", f_sample.read())

    # Place a comment at the specified location to notify user
    comment = "*Attention: This README was automatically generated at {}.*".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    readme_txt = readme_txt.replace("<@generator-comment>", comment)

    with open("README.md", 'w') as f_output:
        f_output.write(readme_txt)

    # insert toc
    with open("README.md", 'r') as f_sample:
        readme_txt = f_sample.read()
        sproc = common.run_linux_cmd("gh-md-toc README.md")
        readme_txt = muninn.text.replace_tags(readme_txt, "TOC", sproc.stdout.decode(
            "utf-8"))

    with open("README.md", 'w') as f_output:
        f_output.write(readme_txt)


if __name__ == "__main__":
    main()