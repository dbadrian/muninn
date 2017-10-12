#! /usr/bin/env python3
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
        logger.debug("Added: %s->%s | All Edges: %s", self.name,
                     node.name, [edge.name for edge in self.parents])

    def add_edge(self, node):
        self.edges.append(node)
        logger.debug("Added: %s->%s | All Edges: %s", self.name,
                     node.name, [edge.name for edge in self.edges])
        node.add_parent(self)


def build_graph(pkgs):
    # Create Nodes of all packages
    graph = {pkg.info["name"]: (Node(pkg.info["name"]),
                                tuple(pkg.info["depends"]["muninn"]))
             for pkg in pkgs.values()}

    # will contain those packages, for which dependencies
    # can not be statisfied, since there is no muninn pkg
    # available
    not_queued_pkgs = []
    for name, (node, dependencies) in graph.items():
        for dependency in dependencies:
            try:
                node.add_edge(graph[dependency][0])
            except KeyError:
                not_queued_pkgs.append(name)
                logger.error("Dependency %s for package %s not found in list.",
                             dependency, name)

    removed_pkgs = []
    for pkg in not_queued_pkgs:
        logger.debug("Removing {} and parents from graph".format(pkg))
        remove_node_from_graph(pkg, graph, removed_pkgs)

    logger.error(
        "Following pkgs were removed as dependencies can not be met: {}"
        .format(removed_pkgs))

    return graph


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
