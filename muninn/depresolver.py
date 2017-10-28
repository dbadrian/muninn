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

import logging

logger = logging.getLogger(__name__)


class CircularDependency(Exception):
    pass


class Node:
    def __init__(self, name):
        self.name = name
        self.edges = []
        self.parents = []

    def add_parent(self, node):
        self.parents.append(node)
        logger.debug("Added (Parent): %s->%s | All Edges: %s", self.name,
                     node.name, [edge.name for edge in self.parents])

    def add_edge(self, node):
        self.edges.append(node)
        logger.debug("Added (Child): %s->%s | All Edges: %s", self.name,
                     node.name, [edge.name for edge in self.edges])
        node.add_parent(self)


def build_graph(desired_pkgs, pkgs):
    # Create Nodes of all desired packages which are already loaded
    graph = {pkgs[pkg_name].info["name"]: (Node(pkgs[pkg_name].info["name"]),
                                tuple(pkgs[pkg_name].info["depends"]["muninn"]))
             for pkg_name, _ in desired_pkgs}

    print(graph)

    # will contain those packages, for which dependencies
    # can not be satisfied, since there is no muninn pkg
    # available
    not_queued_pkgs = []
    # make list of graph as we modify the graph during iteration
    for name, (node, dependencies) in list(graph.items()):
        for dependency in dependencies:
            try:
                node.add_edge(graph[dependency][0])
            except KeyError:
                logger.debug("Loading missing dependency %s", dependency)
                # node for dependencies does not exist yet.
                ret = recursive_dependecies_add(dependency, graph, pkgs)
                if dependency in ret:
                    # add this pkgs as well
                    ret += [name]
                else:
                    # finally add the edge
                    node.add_edge(graph[dependency][0])

                not_queued_pkgs += ret


    logger.debug("Packages not queued: %s", not_queued_pkgs)
    removed_pkgs = []
    for pkg in not_queued_pkgs:
        logger.debug("Removing {} and parents from graph".format(pkg))
        remove_node_from_graph(pkg, graph, removed_pkgs)

    logger.error(
        "Following pkgs were removed as dependencies can not be met: {}"
        .format(removed_pkgs))

    return graph, set(removed_pkgs)

def recursive_dependecies_add(dependency, graph, pkgs):
    if dependency in pkgs:
        pkgs[dependency].load_module(version="latest")
    else:
        return [dependency]

    graph[pkgs[dependency].info["name"]] = (Node(pkgs[dependency].info["name"]),
                                            tuple(pkgs[dependency].info[
                                                      "depends"]["muninn"]))

    not_queued_pkgs = []
    for dep in graph[pkgs[dependency].info["name"]][1]:
        try:
            graph[pkgs[dependency].info["name"]][0].add_edge(graph[dep][0])
        except KeyError:
            logger.debug("Loading missing dependency %s", dep)
            # node for dependencies does not exist yet.
            ret = recursive_dependecies_add(dep, graph, pkgs)
            if dep not in ret:
                graph[pkgs[dependency].info["name"]][0].add_edge(graph[dep][0])
            else:
                ret += [dependency]
            not_queued_pkgs += ret
    return not_queued_pkgs


def remove_node_from_graph(node_name, graph, removed_pkgs):
    node = graph.pop(node_name, None)
    if node:
        for parent in node[0].parents:
            remove_node_from_graph(parent.name, graph, removed_pkgs)
        removed_pkgs.append(node_name)


def resolve_graph(graph):
    install_order = []

    for name, (node, dependencies) in graph.items():
        resolved_order = []
        unresolved_order = []
        try:
            resolve(node, resolved_order, unresolved_order)
        except CircularDependency:
            cd_str = \
                "-->".join([node.name for node in unresolved_order] + [name])
            logger.error("Detected circular dependency: %s\n \
                          Dropping package %s from install queue.",
                         cd_str, name)
        resolved_order_names = [node.name for node in resolved_order]

        for pkg in resolved_order_names:
            if pkg not in install_order:
                install_order.append(pkg)

    logger.debug("Resolved install order {}".format(install_order))
    return(install_order)


def find_dependencies(name=None, graph=None, node=None):
    resolved = []
    unresolved = []
    if node:
        resolve(node, resolved, unresolved)
    elif name and graph:
        resolve(graph[name][0], resolved, unresolved)

    return [node.name for node in resolved][:-1]


def resolve(node, resolved, unresolved):
    """
    https://www.electricmonk.nl/log/2008/08/07/dependency-resolving-algorithm/

    @param      node        Node for which dependecy resolve-order is
                            determined.
    @param      resolved    The ordered list of dependencies to resolve.
    @param      unresolved  Needed for recursion. Ignore.

    @return     { description_of_the_return_value }
    """
    unresolved.append(node)
    for edge in node.edges:
        if edge not in resolved:
            if edge in unresolved:
                raise CircularDependency(
                    'Circular reference detected: %s -> %s' %
                    (node.name, edge.name))
            resolve(edge, resolved, unresolved)
    resolved.append(node)
    unresolved.remove(node)
