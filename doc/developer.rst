.. toctree::

.. highlight:: sh

===============
Developer Guide
===============


Setup Development Environment
=============================

#. Install ``uv``:

   Check https://docs.astral.sh/uv/ for your platform.

#. Install ``tox`` with the ``tox-uv`` plugin:

   ::

      uv tool install tox --with tox-uv


Building Documentation
======================

::

   tox -e doc

Output will be available at ``.tox/doc/tmp/html``. It is recommended to install
the ``webdev`` package:

::

   sudo pip install webdev

So a development web server can serve any location like this:

::

   $ webdev .tox/doc/tmp/html


Running Test Suite
==================

::

   tox -e test
