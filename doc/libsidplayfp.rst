API Documentation
#################

.. py:currentmodule:: libsidplayfp

This module mirrors most of the C++ API of libsidplayfp 1.8. Some methods of the public interfaces are not implemented in the corresponding wrapper classes. These are methods which are meant for internal use, are deprecated or very rarely useful.

SID Player and Configuration
============================

:py:class:`SidPlayfp` is the main interface to play sidtunes and control the emulation. For an example see :doc:`example`.


.. py:class:: SidPlayfp()

    Main interface to libsidplayfp to play tunes.


    .. py:attribute:: SidPlayfp.cia1_timerA

        Get the CIA 1 Timer A programmed value.


    .. py:attribute:: SidPlayfp.config

        Current engine configuration. (see :py:class:`SidConfig`)

    .. py:method:: SidPlayfp.configure()

        Configure engine using :py:attr:`SidPlayfp.config`. An :py:class:`SidPlayfpConfigError` is raised if engine could not be configured.


    .. py:method:: SidPlayfp.debug(enable, file_=None)

        Enable debugging.

        From sidplayfp.h:

            Control debugging.
            Only has effect if library have been compiled
            with the ``--enable-debug`` option.


    .. py:attribute:: SidPlayfp.error

        Current error message.


    .. py:method:: SidPlayfp.fast_forward(percent)

        Set fast-forward factor.

        :param percent: fast-forward factor in percent.
        :type percent: int


    .. py:attribute:: SidPlayfp.info

        Get the current player informations. (see :py:class:`SidInfo`)


    .. py:attribute:: SidPlayfp.is_playing

        Check if the engine is playing or stopped.


    .. py:method:: SidPlayfp.load(tune)

        Load a tune.

        :param tune: sidtune to load
        :type tune: :py:class:`SidTune`
        :raises SidPlayfpLoadError: if an error occurs


    .. py:method:: SidPlayfp.play(buffer, length=None)

        Run the emulation and produce samples to play if a buffer is given. If
        length is not given, it will be calculated from ``len(buffer) // 2``.

        :param buffer: buffer to write samples to
        :type buffer: a mutable buffer
        :param length: length of buffer (assuming 16-bit samples)
        :type length: int
        :returns: number of produced samples
        :rtype: int


    .. py:method:: SidPlayfp.set_roms(kernal, basic=None, character=None)

        Set ROM images.

        :param kernal: Kernal ROM
        :type kernal: buffer
        :param kernal: Basic ROM, generally only needed for BASIC tunes.
        :type kernal: buffer
        :param kernal: character generator ROM
        :type kernal: buffer


    .. py:method:: SidPlayfp.stop()

        Stop the engine.


    .. py:attribute:: SidPlayfp.time

        The current playing time in seconds.


.. py:class:: SidConfig(obj=None)

    An instance of this class is used to transport emulator settings
    to and from the interface class. Writing to any property is allowed
    (and necessary to configure the engine).


    .. py:attribute:: SidConfig.default_c64_model

        Intended c64 model when unknown or forced. (see :py:class:`C64Model`)


    .. py:attribute:: SidConfig.default_sid_model

        Intended sid model when unknown or forced. (see :py:class:`SidModel`)


    .. py:attribute:: SidConfig.fast_sampling

        Faster low-quality emulation (only reSID/fp)


    .. py:attribute:: SidConfig.force_c64_model

        Force the model to :py:attr:`default_c64_model` ignoring tune's
        clock setting.


    .. py:attribute:: SidConfig.force_sid_model

        Force the sid model to :py:attr:`default_sid_model`.


    .. py:attribute:: SidConfig.frequency

        Sampling frequency.


    .. py:attribute:: SidConfig.left_volume

        Left channel volume.


    .. py:attribute:: SidConfig.playback

        Playbak mode. (see :py:class:`Playback`)


    .. py:attribute:: SidConfig.power_on_delay

        Power on delay cycles.


    .. py:attribute:: SidConfig.right_volume

        Right channel volume.


    .. py:attribute:: SidConfig.sampling_method

        Sampling method. (see :py:class:`SamplingMethod`)


    .. py:attribute:: SidConfig.second_sid_address

        address of 2nd sid


    .. py:attribute:: SidConfig.sid_emulation

        Selected sid emulation (:py:class:`SidBuilder`)

        Reading this property always returns a :py:class:`SidBuilder`, however
        as this is an abstract class the internal object is actually one of
        :py:class:`ReSIDfpBuilder`, :py:class:`ReSIDBuilder` or
        :py:class:`HardSIDBuilder`.

        Writing to this property supports any of these classes as it is
        casted internally.


    .. py:attribute:: SidConfig.third_sid_address

        address of 3rd sid


.. py:class:: SidInfo(obj)

    This provides information about the sid engine implementation.


    .. py:attribute:: SidInfo.basic_desc

        Description of the loaded basic ROM image


    .. py:attribute:: SidInfo.channels

        Number of output channels (1-mono, 2-stereo)


    .. py:attribute:: SidInfo.chargen_desc

        Description of the loaded character ROM image


    .. py:attribute:: SidInfo.credits

        Array of library credits


    .. py:attribute:: SidInfo.driver_addr

        Address of the driver


    .. py:attribute:: SidInfo.driver_length

        Size of the driver in bytes


    .. py:attribute:: SidInfo.kernal_desc

        Description of the loaded kernal ROM image


    .. py:attribute:: SidInfo.maxsids

        Number of SIDs supported by this library


    .. py:attribute:: SidInfo.name

        Library name


    .. py:attribute:: SidInfo.power_on_delay

        Power on delay


    .. py:attribute:: SidInfo.speed_string

        Describes the speed current song is running at


    .. py:attribute:: SidInfo.version

        Library version


SidTunes
--------

Sidtunes can be loaded from files using :py:class:`SidTune`. Using its method :py:func:`SidTune.get_info` some information can be gathered about the tune. Note however that sidtunes do not store their intentional playtime. That must be provided separately, e.g. by using a songlength database and :py:class:`SidDatabase`.

.. py:class:: SidTune(filename=None, source_buffer=None)

    Load a sidtune from a file.

    ``filename`` specifies a path to a sidtune to load. If ``source_buffer``
    is given a sidtune is created from that buffer using :py:func:`.read`.
    If neither is given, an error is raised. This is in contrast too the
    underlying C++ library libsidplayfp which allows to create a SidTune
    instance in an invalid state.

    :param filename: path to sidtune
    :type filename: bytes
    :param source_buffer: buffer of complete sidtune
    :type source_buffer: bytes

    :raises SidTuneError: if loading a given tune fails

    From SidTune.h:

        To retrieve data from standard input pass in filename "-".
        If you want to override the default filename extensions use this
        contructor. Please note, that if the specified "fileName"
        does exist and the loader is able to determine its file format,
        this function does not try to append any file name extension.
        See "SidTune.cpp" for the default list of file name extensions.
        You can specify "fileName = 0", if you do not want to
        load a sidtune. You can later load one with open().



    .. py:method:: SidTune.create_MD5()

        Calculates the MD5 hash of the tune.

        :returns: md5 of this tune
        :rtype: bytes


    .. py:method:: SidTune.get_info(song_num=None)

        Retrieve sub-song specific information. If ``song_num`` is None,
        information about the current active song is returned.

        :param song_num: song number get information
        :type song_num: int or None
        :returns: Information about song
        :rtype: :py:class:`SidTuneInfo`


    .. py:method:: SidTune.load(filename)

        Load a sidtune into an existing object from a file.

        :raises SidTuneError: if loading a given tune fails


    .. py:method:: SidTune.read(source_buffer)

        Load a sidtune into an existing object from a buffer.

        :raises SidTuneError: if reading a given tune fails


    .. py:method:: SidTune.select_song(song_num)

        Select subtune. ``song_num=0`` selects the starting song.

        :param song_num: sub-song to load
        :type song_num: int
        :returns: active song number, 0 if no tune is loaded
        :rtype: int


    .. py:attribute:: SidTune.status

        Determine current state of object.
        Upon error condition use :py:attr:`status_string` to get a descriptive
        text string.


    .. py:attribute:: SidTune.status_string

        Error/status message of last operation.


.. py:class:: SidTuneInfo(obj)

    This interface is used to get values from SidTune objects.

    Create instances of this class by calling :py:func:`SidTune.get_info`.


    .. py:attribute:: SidTuneInfo.c64data_len

        Length of raw C64 data without load address.


    .. py:attribute:: SidTuneInfo.clock_speed

        The tune clock speed. (see :py:class:`SidClock`)


    .. py:attribute:: SidTuneInfo.comment_strings

        Tune (MUS) comments.

        :returns: tune information
        :rtype: list


    .. py:attribute:: SidTuneInfo.compatibility

        Compatibility requirements. (see :py:class:`SidCompatibility`)


    .. py:attribute:: SidTuneInfo.current_song

        The tune that has been initialized.


    .. py:attribute:: SidTuneInfo.data_file_len

        Length of single-file sidtune file.


    .. py:attribute:: SidTuneInfo.data_filename

        A first file: e.g. "foo.sid" or "foo.mus".


    .. py:attribute:: SidTuneInfo.fix_load

        Whether load address might be duplicate.


    .. py:attribute:: SidTuneInfo.format_string

        The name of the identified file format.


    .. py:attribute:: SidTuneInfo.info_filename

        A second file: e.g. "foo.str" or None if no second file.


    .. py:attribute:: SidTuneInfo.info_strings

        Return tune informations: Song title, author and release information.

        :returns: tune information
        :rtype: list


    .. py:attribute:: SidTuneInfo.init_addr

        Init Address.


    .. py:attribute:: SidTuneInfo.load_addr

        Load Address.


    .. py:attribute:: SidTuneInfo.path

        Path to sidtune files.


    .. py:attribute:: SidTuneInfo.play_addr

        Play Address.


    .. py:attribute:: SidTuneInfo.reloc_pages

        Number of pages available for relocation.


    .. py:attribute:: SidTuneInfo.reloc_start_page

        First available page for relocation.


    .. py:method:: SidTuneInfo.sid_chip_base(i)

        The SID chip base address(es) used by the sidtune.

        :param i: chip number
        :type i: int
        :rtype: int


    .. py:attribute:: SidTuneInfo.sid_chips

        Get the number of SID chips required by the tune.


    .. py:method:: SidTuneInfo.sid_model(i)

        The SID chip model(s) requested by the sidtune.

        :param i: chip number
        :type i: int
        :rtype: :py:class:`SidModel`


    .. py:attribute:: SidTuneInfo.song_speed

        Intended speed.


    .. py:attribute:: SidTuneInfo.songs

        The number of songs.


    .. py:attribute:: SidTuneInfo.start_song

        The default starting song.


Enumerations
------------

Several enumerations to support :py:class:`SidConfig`, :py:class:`SidInfo` and :py:class:`SidTuneInfo`.


.. py:class:: SidModel

    An enumeration.


    .. py:attribute:: SidModel.UNKNOWN
       :annotation: = 0

        SID model unknown.


    .. py:attribute:: SidModel.MODEL6581
       :annotation: = 1

        MOS6581 required.


    .. py:attribute:: SidModel.MODEL8580
       :annotation: = 2

        MOS8580 required.


    .. py:attribute:: SidModel.ANY
       :annotation: = 3

        Any SID model can be used.


.. py:class:: C64Model

    C64 model


    .. py:attribute:: C64Model.DREAN
       :annotation: = 3

        DREAN


    .. py:attribute:: C64Model.NTSC
       :annotation: = 1

        NTSC


    .. py:attribute:: C64Model.OLD_NTSC
       :annotation: = 2

        Old NTSC


    .. py:attribute:: C64Model.PAL
       :annotation: = 0

        PAL


.. py:class:: Playback

    Mono or stereo playback.


    .. py:attribute:: Playback.MONO
       :annotation: = 1

        Mono playback (1 channel)


    .. py:attribute:: Playback.STEREO
       :annotation: = 2

        Stereo playback (2 channels)


.. py:class:: SamplingMethod

    Sampling method.


    .. py:attribute:: SamplingMethod.INTERPOLATE
       :annotation: = 0

        residfp: ZeroOrderResample


    .. py:attribute:: SamplingMethod.RESAMPLE_INTERPOLATE
       :annotation: = 1

        residfp: TwoPassSincResample


.. py:class:: SidClock

    An enumeration.


    .. py:attribute:: SidClock.ANY
       :annotation: = 3

        Any clock can be used


    .. py:attribute:: SidClock.NTSC
       :annotation: = 2

        NTSC clock required


    .. py:attribute:: SidClock.PAL
       :annotation: = 1

        PAL clock required


    .. py:attribute:: SidClock.UNKNOWN
       :annotation: = 0

        Clock unknown


.. py:class:: SidCompatibility

    An enumeration.


    .. py:attribute:: SidCompatibility.C64
       :annotation: = 0

        File is C64 compatible


    .. py:attribute:: SidCompatibility.PSID
       :annotation: = 1

        File is PSID specific


    .. py:attribute:: SidCompatibility.R64
       :annotation: = 2

        File is Real C64 only


    .. py:attribute:: SidCompatibility.BASIC
       :annotation: = 3

        File requires C64 Basic

Exceptions
----------

.. py:class:: SidError

    Base class for Exceptions from libsidplayfp.


.. py:class:: SidPlayfpConfigError

    Error raised while setting :py:attr:`SidPlayfp.config`.


.. py:class:: SidPlayfpLoadError

    Error raised by :py:func:`SidPlayfp.load` while loading a tune.


.. py:class:: SidTuneError

    Error raised when loading or reading a :py:class:`SidTune` fails.


SidBuilder Classes
==================

To play a SidTune, an emulation of the SID chip is needed. There are three options: :py:class:`ReSIDfpBuilder`, :py:class:`ReSIDBuilder` and :py:class:`HardSIDBuilder` which actually provide an emulation implementation. :py:class:`SidBuilder` is the abstract (only in the C++ implementation) base class of these but does not provide an implementation. You probably should never need to create an instance of this class by yourself.

.. py:class:: SidBuilder(obj)

    Wrapper for sid builders. Base class of :py:class:`ReSIDfpBuilder`,
    :py:class:`ReSIDBuilder` and :py:class:`HardSIDBuilder`.

    :param obj: sid builder to wrap
    :type obj: ``sidbuilder*``

    libsidplayfp offers two additional methods
    ``sidemu *lock(EventContext *env, SidConfig::sid_model_t model);`` and
    ``void unlock(sidemu *device);`` which are not offered by this wrapper
    class. These functions are intended for internal use to provide
    the player with the required SID chips even though they are part of
    ``sidbuilder``'s public interface.


    .. py:attribute:: SidBuilder.avail_devices

        Number of available devices, 0 if  any number is available.


    .. py:method:: SidBuilder.create(sids)

        Create ``sids`` sid emulators.

        :param sids: the number of required sid emulators
        :type sids: int
        :return: number of created sid emulators
        :rtype: int


    .. py:attribute:: SidBuilder.credits

        credits of this sid builder.


    .. py:attribute:: SidBuilder.error

        current error message


    .. py:method:: SidBuilder.filter(enable)

        Toggle sid filter emulation.

        :param enable: Enable of disable filter emulation
        :type enable: bool


    .. py:attribute:: SidBuilder.name

        The builder's name


    .. py:attribute:: SidBuilder.status

        current error status: True if no error occured, False otherwise


    .. py:attribute:: SidBuilder.used_devices

        The number of used devices, 0 if none are used.


.. py:class:: ReSIDfpBuilder(name=None, cast=None, cdata=None)

    ReSIDfp Builder Class, inherits from :py:class:`SidBuilder`.

    If ``name`` passed, a new ReSIDfpBuilder will be created. If ``cast``
    is given, the underlying object will be casted to a
    ``ReSIDfpBuilder`` without further checks. If ``cdata`` is given, it
    will be treated as a cffi-``cdata`` object and casted to a
    ``ReSIDfpBuilder``.

    If a new builder is created this owns that builder object, so be sure that
    the instance of this class is not garbage collected until you don't need
    the builder any more.

    If no new builder is created but just casted, this instance does not own
    the underlying cdata object.

    :param name: Name of new builder (creates new object)
    :type name: str
    :param cast: wrapper class to cast into ReSIDfpBuilder
    :type cast: :py:class:`SidBuilder`
    :param cdata: (for internal use) cdata object to cast into
        ``ReSIDfpBuilder*``
    :type cdata: cffi ``cdata`` (usually ``<cdata 'struct sidbuilder *'>``)


    .. py:method:: ReSIDfpBuilder.filter_6581_curve(filter_curve)

        Set 6581 filter curve.

        :param filter_curve: filterCurve from 0.0 (light) to
            1.0 (dark) (default 0.5)
        :type filter_curve: double


    .. py:method:: ReSIDfpBuilder.filter_8580_curve(filter_curve)

        Set 8580 filter curve.

        :param filter_curve: curve center frequency (default 12500)
        :type filter_curve: double


.. py:class:: ReSIDBuilder(name=None, cast=None, cdata=None)

    ReSID Builder Class

    For an explanation on the parameter see :py:class:`ReSIDfpBuilder`.


    .. py:method:: ReSIDBuilder.bias(dac_bias)
       :module: libsidplayfp

        The bias is given in millivolts, and a maximum reasonable
        control range is approximately -500 to 500.


.. py:class:: HardSIDBuilder(name=None, cast=None, cdata=None)

    HardSID Builder Class

    For an explanation on the parameter see :py:class:`ReSIDfpBuilder`.


Songlength Database Utility
===========================

:py:class:`SidDatabase` can be used to read song lengths from the songlength database (``songlength.txt`` from `HVSC <http://hvsc.c64.org>`_). It is included in libsidplayfp however it is not actually required to play sidtunes.

.. py:class:: SidDatabase()

    An utility class to deal with the songlength database.


    .. py:method:: SidDatabase.close()

        Close the songlength database.


    .. py:attribute:: SidDatabase.error

        Get descriptive error message.


    .. py:method:: SidDatabase.length(tune_or_md5, song_num=None)

        Get the length of the selected subtune in seconds. If a
        :py:class:`SidTune` is passed the length of the currently selected
        subtune is returned.

        :param tune_or_md5: SidTune or md5 of a SidTune
        :type tune_or_md5: :py:class:`SidTune` or bytes
        :param song_num: song number of subtune (required if an md5 is passed)
        :type song_num: ``None`` or int
        :return: tune length in seconds
        :rtype: int
        :raises SidDatabaseError: if length could not be determined


    .. py:method:: SidDatabase.open(filename)

        Open the songlength DataBase.

        :param filename: full path to songlength db
        :raises SidDatabaseError: if songlength db could not be loaded

.. py:class:: SidDatabaseError

    Exception raised by :py:class:`SidDatabase`

Access to internal C wrapper
============================

As libsidplayfp is written in C++, it was necessary to write a wrapper for all methods of all public interface's classes. cffi makes that effort rather simple. All wrapper methods are available from ``libsidplay.lib``, however these are not documented as that api is not guaranteed to be stable. It is only available from source in ``libsidplayfp/libsidplayfp_builder.py``.
An interface to the ffi is provided by ``libsidplayfp.ffi``. This can be used to cast the internal cdata objects.
