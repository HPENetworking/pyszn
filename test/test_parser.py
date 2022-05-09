# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018 Hewlett Packard Enterprise Development LP
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
Test suite for module pyszn.parser.
"""

from textwrap import dedent
from collections import OrderedDict
from logging import getLogger

from deepdiff import DeepDiff


from pyszn.parser import parse_txtmeta


log = getLogger(__name__)


def test_basic_parse():
    """
    Tests parsing of a complete SZN
    """

    topology = """
    # Environment
    [virtual=none awesomeness=medium]

    # Nodes
    [shell=vtysh] sw1 sw2
    [type=host] hs1
    hs2

    # Links
    sw1:1 -- hs1:1
    [attr1=2.1e2 attr2=-2.7e-1] sw1:a -- hs1:a
    [attr1=1 attr2="lorem ipsum" attr3=(1, 3.0, "B")] sw1:4 -- hs2:a
    """

    actual = parse_txtmeta(topology)

    expected = {
        'environment': OrderedDict(
            [('virtual', 'none'), ('awesomeness', 'medium')]
        ),
        'nodes': [
            {
                'attributes': OrderedDict([('type', 'host')]),
                'nodes': ['hs1'],
                'subnodes': [],
                'parent': None,
            },
            {
                'attributes': OrderedDict(),
                'nodes': ['hs2'],
                'subnodes': [],
                'parent': None,
            },
            {
                'attributes': OrderedDict([('shell', 'vtysh')]),
                'nodes': ['sw1'],
                'subnodes': [],
                'parent': None,
            },
            {
                'attributes': OrderedDict([('shell', 'vtysh')]),
                'nodes': ['sw2'],
                'subnodes': [],
                'parent': None,
            },
        ],
        'ports': [
            {
                'ports': [('hs1', '1')],
                'attributes': OrderedDict()
            },
            {
                'ports': [('hs1', 'a')],
                'attributes': OrderedDict()
            },
            {
                'ports': [('hs2', 'a')],
                'attributes': OrderedDict()
            },
            {
                'ports': [('sw1', '1')],
                'attributes': OrderedDict()
            },
            {
                'ports': [('sw1', '4')],
                'attributes': OrderedDict()
            },
            {
                'ports': [('sw1', 'a')],
                'attributes': OrderedDict()
            },
        ],
        'links': [
            {
                'attributes': OrderedDict(),
                'endpoints': (('sw1', '1'), ('hs1', '1'))
            },
            {
                'attributes': OrderedDict(
                    [
                        ('attr1', 1), ('attr2', 'lorem ipsum'),
                        ('attr3', [1, 3.0, 'B'])
                    ]
                ),
                'endpoints': (('sw1', '4'), ('hs2', 'a'))
            },
            {
                'attributes': OrderedDict(
                    [
                        ('attr1', 210.0),
                        ('attr2', -0.27)
                    ]
                ),
                'endpoints': (('sw1', 'a'), ('hs1', 'a'))
            },
        ]
    }

    assert not DeepDiff(actual, expected)


def test_autonode():
    """
    Test the automatic creation of implicit nodes
    """

    topology = """
    sw1:port1
    """

    actual = parse_txtmeta(topology)

    expected = {
        'environment': OrderedDict(),
        'nodes': [{
            'attributes': OrderedDict(),
            'nodes': ['sw1'],
            'subnodes': [],
            'parent': None,
        }],
        'ports': [{'ports': [('sw1', 'port1')], 'attributes': OrderedDict()}],
        'links': []
    }

    assert not DeepDiff(actual, expected)


def test_multiline_list():
    """
    Test the support for multiline list attributes
    """
    topology = """
    # Environment
    [
        virtual=none
        awesomeness=medium
        float=1.0
        list=(
            1,
            3.14,
            True
        )
    ]
    """
    actual = parse_txtmeta(topology)

    expected = {
        'environment': OrderedDict(
            [
                ('virtual', 'none'), ('awesomeness', 'medium'), ('float', 1.0),
                ('list', [1, 3.14, True])
            ]
        ),
        'nodes': [],
        'ports': [],
        'links': []
    }

    assert not DeepDiff(actual, expected)


def test_multiline_text():
    """
    Test the support for multiline text attributes
    """
    topology = '''
    # Environment
    [
        virtual=none
        awesomeness=medium
        float=1.0
        multiline_text=```
            Buenos Aires
            se ve tan susceptible
            Es el destino de furia, es
                lo que en sus caras persiste
        ```
    ]
    '''
    actual = parse_txtmeta(topology)

    expected = {
        'environment': OrderedDict(
            [
                ('virtual', 'none'),
                ('awesomeness', 'medium'),
                ('float', 1.0),

                # Multiline string attribute values are parsed using
                # textwrap.dedent()
                (
                    'multiline_text',
                    dedent("""
                        Buenos Aires
                        se ve tan susceptible
                        Es el destino de furia, es
                            lo que en sus caras persiste
                    """)
                )
            ]
        ),
        'nodes': [],
        'ports': [],
        'links': []
    }

    assert not DeepDiff(actual, expected)


def test_attributes():
    """
    Test that attributes should just be added to the nodes on the same line
    """
    topology = """
    [attr=value] hs1 hs3
    hs2
    """

    actual = parse_txtmeta(topology)

    expected = {
        'environment': OrderedDict(),
        'nodes': [
            {
                'attributes': OrderedDict([('attr', 'value')]),
                'nodes': ['hs1'],
                'subnodes': [],
                'parent': None,
            },
            {
                'attributes': OrderedDict(),
                'nodes': ['hs2'],
                'subnodes': [],
                'parent': None,
            },
            {
                'attributes': OrderedDict([('attr', 'value')]),
                'nodes': ['hs3'],
                'subnodes': [],
                'parent': None,
            },
        ],
        'ports': [],
        'links': []
    }

    assert not DeepDiff(actual, expected)


def test_single():
    """
    Test that a single line string (no new lines '\\n') is parsed
    """
    topology = """[attr=value] hs1"""

    actual = parse_txtmeta(topology)

    expected = {
        'environment': OrderedDict(),
        'nodes': [
            {
                'attributes': OrderedDict([('attr', 'value')]),
                'nodes': ['hs1'],
                'subnodes': [],
                'parent': None,
            },
        ],
        'ports': [],
        'links': []
    }

    assert not DeepDiff(actual, expected)


def test_subnodes():
    """
    Test the capability of specifying subnodes.
    """
    topology = """
    # Level 0  nodes
    [color=red] switch1
    [color=blue] switch2

    # Level 1 node
    [flavor=vanilla] switch1>card1

    # Level 2 node
    [flavor="blue-berry"] switch1>card1>subcard1

    # Links
    # Link from a level 0 node to a level 0 node
    [link_mood=happy] switch2:port1 -- switch1:port1

    # Link from a level 0 node to a level 1 node
    switch2:port2 -- switch1>card1:port1

    # Link from a level 0 node to a level 2 node
    switch2:port3 -- switch1>card1>subcard1:port1

    # Ports
    # Level 0 port
    [speed_gbps=10] switch1:port1

    # Level 1 port
    [speed_gbps=20] switch1>card1:port1

    # Level 2 port
    [speed_gbps=30] switch1>card1>subcard1:port1
    """
    actual = parse_txtmeta(topology)

    expected = {
        'environment': OrderedDict(),

        # Nodes are sorted alphabetically by node name
        'nodes': [
            {
                'attributes': OrderedDict([('color', 'red')]),
                'nodes': ['switch1'],
                'subnodes': ['switch1>card1'],
                'parent': None,
            },
            {
                'attributes': OrderedDict([('flavor', 'vanilla')]),
                'nodes': ['switch1>card1'],
                'subnodes': ['switch1>card1>subcard1'],
                'parent': 'switch1',
            },
            {
                'attributes': OrderedDict([('flavor', 'blue-berry')]),
                'nodes': ['switch1>card1>subcard1'],
                'subnodes': [],
                'parent': 'switch1>card1',
            },
            {
                'attributes': OrderedDict([('color', 'blue')]),
                'nodes': ['switch2'],
                'subnodes': [],
                'parent': None,
            },

        ],

        # Ports are sorted alphabetically by the ports field
        'ports': [
            {
                'ports': [('switch1', 'port1')],
                'attributes': OrderedDict([('speed_gbps', 10)])
            },
            {
                'ports': [('switch1>card1', 'port1')],
                'attributes': OrderedDict([('speed_gbps', 20)])
            },
            {
                'ports': [('switch1>card1>subcard1', 'port1')],
                'attributes': OrderedDict([('speed_gbps', 30)])
            },
            {
                'ports': [('switch2', 'port1')],
                'attributes': OrderedDict()
            },
            {
                'ports': [('switch2', 'port2')],
                'attributes': OrderedDict()
            },
            {
                'ports': [('switch2', 'port3')],
                'attributes': OrderedDict()
            },
        ],

        # Links are sorted alphabetically by the endpoints field
        'links': [
            {
                'attributes': OrderedDict(
                    [
                        ('link_mood', 'happy'),
                    ]
                ),
                'endpoints': (('switch2', 'port1'), ('switch1', 'port1'))
            },
            {
                'attributes': OrderedDict(),
                'endpoints': (('switch2', 'port2'), ('switch1>card1', 'port1'))
            },
            {
                'attributes': OrderedDict(),
                'endpoints': (
                    ('switch2', 'port3'), ('switch1>card1>subcard1', 'port1')
                )
            },
        ]
    }
    assert not DeepDiff(actual, expected)
