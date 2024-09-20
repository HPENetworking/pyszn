======================
Python package for SZN
======================

A Python package for the Simplified Zone Notation standard.


Documentation
=============

    https://pyszn.readthedocs.org/


Changelog
=========


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

   Copyright (C) 2016-2024 Hewlett Packard Enterprise Development LP

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
