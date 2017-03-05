libsidplayfp API Documentation
##############################

.. py:currentmodule:: libsidplayfp

This module mirrors mostly the C++ API of libsidplayfp 1.8. Some methods of the public interfaces ar enot implemented in the corresponding wrapper class. These are methods which are meant for internal use or are very rarely useful. Additionally no methods marked as deprecated are implemented.

SID Player and Configuration
============================

:py:class:`SidPlayfp` is the main interface to play sidtunes and control the emulation. For an example see :doc:`example`.

.. autoclass:: SidPlayfp
    :members:


.. autoclass:: SidConfig
    :members:

.. autoclass:: SidInfo
    :members:


SidTunes
--------

Sidtunes can be loaded from files using :py:class:`SidTune`. Using its method :py:func:`SidTune.get_info` some information can be gathered about the tune. Note however that sidtunes do not store their intentional playtime. That must be provided separately, e.g. by using a songlength database and :py:class:`SidDatabase`.

.. autoclass:: SidTune
    :members:

.. autoclass:: SidTuneInfo
    :members:

Enumerations
------------

Several enumerations to support :py:class:`SidConfig`, :py:class:`SidInfo` and :py:class:`SidTuneInfo`.

.. autoclass:: SidModel
    :members:

.. autoclass:: C64Model
    :members:

.. autoclass:: Playback
    :members:

.. autoclass:: SamplingMethod
    :members:

.. autoclass:: SidClock
    :members:

.. autoclass:: SidCompatibility
    :members:

Exceptions
----------

.. autoclass:: SidError
    :members:

.. autoclass:: SidPlayfpConfigError
    :members:

.. autoclass:: SidPlayfpLoadError
    :members:


SidBuilder Classes
==================

To play a SidTune, an emulation of the SID chip is needed. There are three options: :py:class:`ReSIDfpBuilder`, :py:class:`ReSIDBuilder` and :py:class:`HardSIDBuilder` which actually provide an emulation implementation. :py:class:`SidBuilder` is the abstract (only in the C++ implementation) base class of these but does not provide an implementation. You probably should never need to create an instance of this class by yourself.

.. autoclass:: SidBuilder
    :members:

.. autoclass:: ReSIDfpBuilder
    :members:

.. autoclass:: ReSIDBuilder
    :members:

.. autoclass:: HardSIDBuilder
    :members:


Songlength Database Utility
===========================

:py:class:`SidDatabase` can be used to read song lengths from the songlength database (``songlength.txt`` from `HVSC <http://hvsc.c64.org>`_). It is included in libsidplayfp however it is not actually required to play sidtunes.

.. autoclass:: SidDatabase
    :members:

.. autoclass:: SidDatabaseError
    :members:
