=================
SZN Python Parser
=================

A Python package for parsing the Simplified Zone Notation (SZN) format.


Documentation
=============

    https://pyszn.readthedocs.org/


Changelog
=========


1.8.1 (2026-03-12)
------------------

New
~~~

- Adds a test for find_topology_in_python, specifically for the TOPOLOGY_ID
  feature. [Carlos Jenkins]

Fix
~~~

- Fixes find_topology_in_python, a generator was being consumed in the first
  comparison and then it was empty in the second one, now a comprehension is
  used instead.
  [Carlos Jenkins]

1.8.0 (2026-03-11)
------------------

New
~~~

- Adds GitHub Actions workflow to run tests on pull request.
  [Carlos Jenkins]

Changes
~~~~~~~

- Updates project to use uv, pyproject.toml and removes setup.py.
  [Carlos Jenkins]
- Updated the find_topology_in_python to use modern Python, be deterministic
  and fixed documentation. [Carlos Jenkins]

Fix
~~~

- Fixes pyparsing deprecation warnings. [Carlos Jenkins]
- Fixes documentation build. [Carlos Jenkins]

1.7.1 (2025-07-03)
------------------

Fix
~~~

- Fix an issue where the attribute injection parser aborted processing a
  injection rule when it finds a non-topology file in the expanded rule files.
  Now it continues processing the same rule with the next file.
  [Sergio Salazar]

1.7.0 (2024-10-04)
------------------

New
~~~

- Nodes, ports and links are now ordered using natural sorter. [Carlos Jenkins]

1.6.0 (2022-06-07)
------------------

New
~~~

- Add the capability to specify subnodes by using ´node>subnode´ syntax.
  [Sergio Salazar]
- Add the capability to specify a multiline text as value of an
  attribute by using \`\`\` [Sergio Salazar]

1.5.0 (2021-11-04)
------------------

Changes
~~~~~~~

- Up to a 10x speedup when parsing attribute injection [Max Nedorezov]

1.4.0 (2021-05-21)
------------------

New
~~~

- Support parse topology from a 'TOPOLOGY_ID' [Jose Martinez]

1.3.0 (2020-10-05)
------------------

New
~~~

- Allow user to skip paths using fnmatch [David Diaz]

1.2.0 (2019-06-11)
------------------

New
~~~

- Support for lists and floats types [Eduardo Mora]

1.1.1 (2018-11-21)
------------------

Changes
~~~~~~~

- Parser supports multiline attributes. [Javier Peralta]

1.1.0 (2018-11-09)
------------------

Changes
~~~~~~~

- Dropped support for Python 2.7. [Carlos Jenkins]

Fix
~~~

- Fix grammar description for pyparsing > 2.2.2. [Carlos Jenkins]

1.0.0 (2017-11-02)
------------------

Initial public release.

New
~~~

- Inject support links ports and env. [Javier Peralta]


License
=======

.. code-block:: text

   Copyright (C) 2016-2026 Hewlett Packard Enterprise Development LP

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing,
   software distributed under the License is distributed on an
   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
   KIND, either express or implied.  See the License for the
   specific language governing permissions and limitations
   under the License.
