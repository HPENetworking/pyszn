# Copyright (C) 2015-2025 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
SZN parser module.

This module takes care of parsing a topology meta-description written in SZN.

This topology representation format allows to quickly specify simple topologies
that are only composed of simple nodes, ports and links between them. For a
more programmatic format consider the ``metadict`` format or using the
:class:`pynml.manager.ExtendedNMLManager` directly.

The format for the textual description of a topology is similar to Graphviz
syntax and allows to define nodes and ports with shared attributes and links
between two endpoints with shared attributes too.

::

    # Environment
    [kernel="3.13.0-77-generic"]

    # Nodes
    [type=switch attr1=1] sw1 sw2
    hs1

    # Ports
    [speed=1000] sw1:3 sw2:3

    # Links
    [linkattr1=20] sw1:a -- sw2:a
    [linkattr2=40] sw1:3 -- sw2:3

In the above example two nodes with the attributes ``type`` and ``attr1`` are
specified. Then a third node `hs1` with no particular attributes is defined.
Later, we specify some attributes (speed) for a couple of ports. In the same
way, a link between endpoints MAY have attributes. An endpoint is a combination
of a node and a port name.
"""

import logging
from re import split
from pathlib import Path
from copy import deepcopy
from textwrap import dedent
from traceback import format_exc
from collections import OrderedDict

from pyparsing import (
    Word, Literal, QuotedString,
    ParserElement, alphas, nums, alphanums,
    Group, OneOrMore, Optional,
    LineEnd, Suppress, LineStart, restOfLine, CaselessLiteral, Combine
)

log = logging.getLogger(__name__)


def naturalkey(element):
    """
    Return a tuple with the string and integer components of a given string.

    For example::

        naturalkey('node01') -> ('node', 1)

    :param str element: The string to decompose.

    :return: The string and integer components of the string.
    :rtype: tuple
    """
    return tuple(
        int(token) if token.isdigit() else token.lower()
        for token in split('([0-9]+)', element)
    )


class ParseException(Exception):
    """
    Custom exception thrown by the parser if it was unable to parse a SZN
    string.

    :var lineno: Line number of the parsing error.
    :var raw_line: Raw line that failed to be parsed.
    :var exc: Internal failure traceback of the parser.
    """

    def __init__(self, lineno, raw_line, exc):
        super(ParseException, self).__init__(
            'Unable to parse line #{}: "{}"'.format(
                lineno, raw_line
            )
        )
        self.lineno = lineno
        self.raw_line = raw_line
        self.exc = exc


def build_parser():
    """
    Build a pyparsing parser for our custom topology description language.

    :return: A pyparsing parser.
    :rtype: pyparsing.MatchFirst
    """
    ParserElement.set_default_whitespace_chars(' \t')
    nl = Suppress(LineEnd())
    inumber = Word(nums).set_parse_action(lambda toks: int(toks[0]))
    fnumber = (
        Combine(
            Optional('-') + Word(nums) + '.' + Word(nums)
            + Optional('E' | 'e' + Optional('-') + Word(nums))
        )
    ).set_parse_action(lambda toks: float(toks[0]))
    boolean = (
        CaselessLiteral('true') | CaselessLiteral('false')
    ).set_parse_action(lambda s, loc, toks: toks[0].casefold() == 'true')
    comment = Literal('#') + restOfLine + nl
    text = QuotedString('"')

    multiline_text = QuotedString('```', multiline=True)
    multiline_text.add_parse_action(lambda t: dedent(t[0]))

    identifier = Word(alphas, alphanums + '_')
    empty_line = LineStart() + LineEnd()
    item_list = (
        (text | fnumber | inumber | boolean)
        + Optional(Suppress(',')) + Optional(nl)
    )
    custom_list = (
        Suppress('(') + Optional(nl) + Group(OneOrMore(item_list))
        + Optional(nl) + Suppress(')')
    ).set_parse_action(lambda tok: tok.as_list())
    attribute = Group(
        identifier('key') + Suppress(Literal('='))
        + (
            custom_list | multiline_text | text | fnumber
            | inumber | boolean | identifier
        )('value')
        + Optional(nl)
    )
    attributes = (
        Suppress(Literal('['))
        + Optional(nl)
        + OneOrMore(attribute)
        + Suppress(Literal(']'))
    )

    node = Word(alphas, alphanums + '_' + '>')('node')

    port = Group(
        node + Suppress(Literal(':')) + (identifier | inumber)('port')
    )
    link = Group(
        port('endpoint_a') + Suppress(Literal('--')) + port('endpoint_b')
    )

    environment_spec = (
        attributes + nl
    ).set_results_name('env_spec', list_all_matches=True)
    nodes_spec = (
        Group(
            Optional(attributes)('attributes')
            + Group(OneOrMore(node))('nodes')
        ) + nl
    ).set_results_name('node_spec', list_all_matches=True)
    ports_spec = (
        Group(
            Optional(attributes)('attributes')
            + Group(OneOrMore(port))('ports')
        ) + nl
    ).set_results_name('port_spec', list_all_matches=True)
    link_spec = (
        Group(
            Optional(attributes)('attributes') + link('links')
        ) + nl
    ).set_results_name('link_spec', list_all_matches=True)

    statements = OneOrMore(
        comment
        | link_spec
        | ports_spec
        | nodes_spec
        | environment_spec
        | empty_line
    )
    return statements


def parse_txtmeta(txtmeta):
    """
    Parse a textual description of a topology and return a dictionary of it's
    elements.

    :param str txtmeta: The textual meta-description of the topology.
    :rtype: dict
    :return: Topology as dictionary.
    """
    statement = build_parser()
    data = {
        'environment': OrderedDict(),
        'nodes': [],
        'ports': [],
        'links': [],
    }

    parsed_result = statement.parse_string(txtmeta)

    # Process environment line
    if 'env_spec' in parsed_result:
        if len(parsed_result['env_spec']) > 1:
            raise Exception(
                'Multiple declaration of environment attributes: '
                '{}'.format(parsed_result['env_spec'][1])
            )
        for attr in parsed_result['env_spec'][0]:
            data['environment'][attr.key] = attr.value[0]

    # Process the links
    if 'link_spec' in parsed_result:
        for parsed in parsed_result['link_spec']:
            link = parsed[0].links
            attrs = OrderedDict()
            if "attributes" in parsed[0]:
                for attr in parsed[0].attributes:
                    attrs[attr.key] = attr.value[0]
            data['links'].append({
                'endpoints': (
                    (str(link.endpoint_a.node), str(link.endpoint_a.port)),
                    (str(link.endpoint_b.node), str(link.endpoint_b.port)),
                ),
                'attributes': attrs,
            })

            data['nodes'].append({
                'nodes': [
                    str(link.endpoint_a.node), str(link.endpoint_b.node)
                ],
                'attributes': OrderedDict(),
            })
            data['ports'].append({
                'ports': [
                    (str(link.endpoint_a.node), str(link.endpoint_a.port)),
                    (str(link.endpoint_b.node), str(link.endpoint_b.port))
                ],
                'attributes': OrderedDict(),
            })

    # Process the ports
    if 'port_spec' in parsed_result:
        for parsed in parsed_result['port_spec']:
            ports = parsed[0].ports
            attrs = OrderedDict()
            if "attributes" in parsed[0]:
                for attr in parsed[0].attributes:
                    attrs[attr.key] = attr.value[0]
            data['ports'].append({
                'ports': [
                    (str(port.node), str(port.port)) for port in ports
                ],
                'attributes': attrs,
            })
            data['nodes'].append({
                'nodes': [str(port.node) for port in ports],
                'attributes': OrderedDict(),
            })

    # Process the nodes
    if 'node_spec' in parsed_result:
        for parsed in parsed_result['node_spec']:
            nodes = parsed[0].nodes
            attrs = OrderedDict()
            if 'attributes' in parsed[0]:
                for attr in parsed[0].attributes:
                    attrs[attr.key] = attr.value[0]
            data['nodes'].append({
                'nodes': [str(node) for node in nodes],
                'attributes': attrs,
            })

    # Remove duplicate data created implicitly
    temp_nodes = OrderedDict()
    for node_list in data['nodes']:
        for node in node_list['nodes']:
            if node not in temp_nodes.keys():
                temp_nodes[node] = {
                    'attributes': deepcopy(node_list['attributes']),
                    'nodes': [node],
                    'subnodes': []
                }
            else:
                temp_nodes[node]['attributes'].update(node_list['attributes'])

            depth = node.count('>')
            parent = None if depth == 0 else node.rsplit('>', 1)[-2]
            temp_nodes[node]['parent'] = parent
            temp_nodes[node]['depth'] = depth

    for node, spec in sorted(
        temp_nodes.items(), key=lambda t: t[1]['depth'], reverse=True
    ):
        parent = spec['parent']
        if parent is not None:
            parent_node = temp_nodes[parent]
            siblings = parent_node['subnodes']
            siblings.append(node)

        del spec['depth']

    temp_ports = OrderedDict()
    for port_list in data['ports']:
        for port in port_list['ports']:
            if port not in temp_ports.keys():
                temp_ports[port] = deepcopy(port_list['attributes'])
            else:
                temp_ports[port].update(port_list['attributes'])

    data['nodes'] = [
        {
            'nodes': [k],
            'attributes': v['attributes'],
            'subnodes': v['subnodes'],
            'parent': v['parent'],
        }
        # Sort by node name
        for k, v in sorted(
            temp_nodes.items(),
            key=lambda e: naturalkey(e[0]),
        )
    ]

    data['ports'] = [
        {'ports': [k], 'attributes': v}
        # Sort by node name and port name ('node01', 'port01')
        for k, v in sorted(
            temp_ports.items(),
            key=lambda e: tuple(
                naturalkey(part)
                for part in e[0]
            ),
        )
    ]

    data['links'] = sorted(
        data['links'],
        # Sort by endpoints (('node01', 'port01'), ('node02', 'port02'))
        key=lambda e: tuple(
            tuple(
                naturalkey(subpart)
                for subpart in part
            )
            for part in e['endpoints']
        )
    )

    return data


def find_topology_in_python(filename, szn_dir=None, encoding='utf-8'):
    """
    Find the topology definition inside a Python file.

    This function searches for a variable named TOPOLOGY or TOPOLOGY_ID inside
    the given Python file. If TOPOLOGY is found, it's value is returned
    directly. If TOPOLOGY_ID is found instead, the function searches for a file
    named <TOPOLOGY_ID>.szn inside the given szn_dir list of paths. If found,
    the content of that file is returned.

    This helper functions build a AST tree a grabs the variable from it. Thus,
    the Python code isn't executed.

    :param Path filename: Path to file to search for TOPOLOGY or TOPOLOGY_ID.
    :param list szn_dir: List of paths to directories where \\*.szn files are
     located.
    :param str encoding: Encoding used to read the files.

    :return: The value of the TOPOLOGY variable if found, None otherwise.
    :rtype: str or None
    """
    import ast

    # Backward compatibility for string paths
    if not isinstance(filename, Path):
        filename = Path(filename)
    if szn_dir is not None:
        szn_dir = [
            Path(path)
            if not isinstance(path, Path)
            else path
            for path in szn_dir
        ]

    try:
        # Parse the Python file to extract the TOPOLOGY or TOPOLOGY_ID variable
        tree = ast.parse(filename.read_text(encoding=encoding))

        # Iterate over the AST nodes to find our variable
        for node in ast.iter_child_nodes(tree):

            # Check if the node is an assignment, if not, skip it
            if not isinstance(node, ast.Assign):
                continue

            # Get the list of assignment targets
            targets = (targets.id for targets in node.targets)

            # Check if we have a TOPOLOGY variable
            if 'TOPOLOGY' in targets:

                # This used to be node.value.s in Python 3.7 and earlier
                # But was deprecated in favor of node.value.value in
                # Python 3.8+
                return node.value.value

            # Check if we have a TOPOLOGY_ID variable
            elif 'TOPOLOGY_ID' in targets:

                if not szn_dir:
                    raise RuntimeError(
                        'Found a TOPOLOGY_ID, but no SZN search '
                        'path was defined'
                    )

                # Grab the reference to the external file
                topology_id = node.value.value

                # Iterate over the search paths to find the referenced file
                # Iteration is done following the explicit order of the list
                # So the user can prioritize paths if needed
                for search_path in szn_dir:

                    # According to Python documentation, Path.glob is not
                    # deterministic, so we need to sort the results to have a
                    # predictable behavior
                    for filename in sorted(
                        search_path.glob(f'{topology_id}.szn'),
                        # Length first (shortest path)
                        # Natural sorting tie-breaker
                        key=lambda path: (
                            len(str(path)),
                            naturalkey(str(path)),
                        )
                    ):
                        return filename.read_text(encoding=encoding)

                raise FileNotFoundError(
                    f'Topology file with ID {topology_id} could not be found'
                )

    except Exception:
        log.error(format_exc())
    return None


__all__ = [
    'ParseException',
    'parse_txtmeta',
    'find_topology_in_python'
]
