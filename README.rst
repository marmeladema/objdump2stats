=============
objdump2stats
=============

---------------

:Author: `Elie ROUDNINSKI <mailto:xademax@gmail.com>`_

**objdump2stats** is a pure Python package that compute statistics from objdump disassembly output.

.. contents::
    :backlinks: none

.. sectnum::

Installation
============

Requirements
------------

**objdump2stats** requires Python 3. It has been tested on Python 3.8 on Linux.

From github
-----------

You can clone this repository and install it with setuptools directly::

    $ python3 setup.py install --user

From pip
--------

As every pip available package, you can install it easily with the pip package::

    $ python3 -m pip install --user objdump2stats

Usage
=====

Just pipe the standard output of `objdump` to objdump2stats's standard input::

    $ objdump -d /bin/false |  objdump2stats

This should print a JSON document with various information gathered from objdump.
