# Copyright (C) 2026 Hewlett Packard Enterprise Development LP
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
Test suite for find_topology_in_python function.
"""

from pathlib import Path


FILES = Path(__file__).parent / 'files'
SZNDIR = FILES / 'topologies'


def test_find_topology_in_python():
    """
    Test that find_topology_in_python correctly identifies the topology
    defined in a Python file.
    """
    from pyszn.parser import find_topology_in_python

    # Found in python file (TOPOLOGY)
    topology = find_topology_in_python(
        FILES / 'topodef.py',
        szn_dir=[SZNDIR],
    )
    assert topology is not None

    # Found in python file (TOPOLOGY_ID)
    topology_a = find_topology_in_python(
        FILES / 'topofile1.py',
        szn_dir=[SZNDIR],
    )
    assert topology_a is not None

    topology_b = find_topology_in_python(
        FILES / 'topofile2.py',
        szn_dir=[SZNDIR],
    )
    assert topology_b is not None

    # Topology not found
    topology_c = find_topology_in_python(
        FILES / 'topofile3.py',
        szn_dir=[SZNDIR],
    )
    assert topology_c is None

    # Bad Python file
    topology_d = find_topology_in_python(
        FILES / 'badfile.py',
        szn_dir=[SZNDIR],
    )
    assert topology_d is None
