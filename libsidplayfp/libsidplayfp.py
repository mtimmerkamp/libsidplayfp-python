#!/usr/bin/env python3
import os
from enum import Enum

from libsidplayfp._libsidplayfp import ffi, lib


class SidPlayfpError(Exception):
    """Base class for Exceptions from libsidplayfp."""
    pass


def _property_builder(prefix):
    """
    Internally used method to build a method that creates read-only properties.
    """
    def generate_property(name, result_wrapper=None, **kwargs):
        def getter(self):
            func = getattr(lib, '{}{}'.format(prefix, name))
            if result_wrapper is None:
                return func(self.obj)
            else:
                return result_wrapper(func(self.obj))

        return property(getter, **kwargs)

    return generate_property


class SidPlayfpConfigError(SidPlayfpError):
    """Error raised while setting :py:attr:`SidPlayfp.config`."""
    pass


class SidPlayfpLoadError(SidPlayfpError):
    """Error raised by :py:func:`SidPlayfp.load` while loading a tune."""
    pass


class SidPlayfp:
    """Main interface to libsidplayfp to play tunes."""

    def __init__(self):
        obj = lib.sidplayfp_new()
        self.obj = ffi.gc(obj, lib.sidplayfp_destroy)

    @property
    def config(self):
        """
        Current engine configuration. (see :py:class:`SidConfig`)
        Set to configure engine, an :py:class:`SidPlayfpConfigError`
        is raised if engine could not be configured.
        """
        return SidConfig(lib.sidplayfp_getConfig(self.obj))

    @config.setter
    def config(self, config):
        success = lib.sidplayfp_setConfig(self.obj, config.obj)

        if not success:
            raise SidPlayfpConfigError(self.error)

    @property
    def info(self):
        """Get the current player informations. (see :py:class:`SidInfo`)"""
        return SidInfo(lib.sidplayfp_info(self.obj))

    @property
    def error(self):
        """Current error message."""
        return ffi.string(lib.sidplayfp_error(self.obj))

    def fast_forward(self, percent):
        """
        Set fast-forward factor.

        :param percent: fast-forward factor in percent.
        :type percent: int
        """
        return lib.sidplayfp_fastForward(self.obj, percent)

    def load(self, tune):
        """
        Load a tune.

        :param tune: sidtune to load
        :type tune: :py:class:`SidTune`
        :raises SidPlayfpLoadError: if an error occurs
        """
        success = lib.sidplayfp_load(self.obj, tune.obj)

        if not success:
            raise SidPlayfpLoadError(self.error)

    def play(self, buffer):
        """
        Run the emulation and produce samples to play if a buffer is given.

        :param buffer: buffer to write samples to
        :type buffer: a mutable buffer
        :returns: number of produced samples
        :rtype: int
        """
        buf = ffi.from_buffer(buffer)
        buf = ffi.cast('short*', buf)
        buf_len = len(buffer) // 2  # 2 byte = 1 short
        return lib.sidplayfp_play(self.obj, buf, buf_len)

    @property
    def is_playing(self):
        """Check if the engine is playing or stopped."""
        return lib.sidplayfp_isPlaying(self.obj)

    def stop(self):
        """Stop the engine."""
        lib.sidplayfp_stop(self.obj)

    def debug(self, enable, file_=None):
        """
        Enable debugging.

        From sidplayfp.h:

            Control debugging.
            Only has effect if library have been compiled
            with the --enable-debug option.
        """
        lib.sidplayfp_debug(self.obj, enable, file_)

    def mute(self, sid_num, voice, enable):
        lib.sidplayfp_mute(self.obj, sid_num, voice, enable)

    @property
    def time(self):
        """The current playing time in seconds."""
        return lib.sidplayfp_time(self.obj)

    def set_roms(self, kernal, basic=None, character=None):
        """
        Set ROM images.

        :param kernal: Kernal ROM
        :type kernal: buffer
        :param kernal: Basic ROM, generally only needed for BASIC tunes.
        :type kernal: buffer
        :param kernal: character generator ROM
        :type kernal: buffer
        """
        def handle_buffer(buff):
            if buff is None:
                buff = ffi.new('uint8_t[]', 0)
            else:
                buff = ffi.cast('uint8_t*', ffi.from_buffer(buff))
            return buff

        kernal = handle_buffer(kernal)
        basic = handle_buffer(basic)
        character = handle_buffer(character)

        lib.sidplayfp_setRoms(self.obj, kernal, basic, character)

    @property
    def cia1_timerA(self):
        """Get the CIA 1 Timer A programmed value."""
        return lib.sidplayfp_getCia1TimerA(self.obj)


class SidTune:
    """
    Load a sidtune from a file.

    ``filename`` specifies a path to a sidtune to load. If ``source_buffer``
    is given a sidtune is created from that buffer using :py:func:`.read`.
    If neither is given, an "empty" tune is created on which :py:func:`load`
    or :py:func:`read` can be called.

    :param filename: path to sidtune
    :type filename: bytes
    :param source_buffer: buffer of complete sidtune
    :type source_buffer: bytes

    From SidTune.h:

        To retrieve data from standard input pass in filename "-".
        If you want to override the default filename extensions use this
        contructor. Please note, that if the specified "fileName"
        does exist and the loader is able to determine its file format,
        this function does not try to append any file name extension.
        See "SidTune.cpp" for the default list of file name extensions.
        You can specify "fileName = 0", if you do not want to
        load a sidtune. You can later load one with open().

    """

    MD5_LENGTH = lib.MD5_LENGTH

    def __init__(self, filename=None, source_buffer=None):
        filename_exts = ffi.cast('char**', 0)

        if source_buffer is not None:
            obj = lib.SidTune_new_from_buffer(
                ffi.from_buffer(source_buffer), len(source_buffer))
        elif filename is None:
            filename = ffi.cast('char*', 0)
            obj = lib.SidTune_new_from_filename(filename, filename_exts, False)
        else:
            filename_exts = ffi.cast('char**', 0)
            sep_is_slash = os.sep == '/'

            obj = lib.SidTune_new_from_filename(
                filename, filename_exts, sep_is_slash)

        self.obj = ffi.gc(obj, lib.SidTune_destroy)

    def load(self, filename):
        """Load a sidtune into an existing object from a file."""
        sep_is_slash = os.sep == '/'
        lib.SidTune_load(self.obj, filename, sep_is_slash)

    def read(self, source_buffer):
        """Load a sidtune into an existing object from a buffer."""
        lib.SidTune_read(
            self.obj, ffi.from_buffer(source_buffer), len(source_buffer))

    def select_song(self, song_num):
        """
        Select subtune. ``song_num=0`` selects the starting song.

        :param song_num: sub-song to load
        :type song_num: int
        :returns: active song number, 0 if no tune is loaded
        :rtype: int
        """
        return lib.SidTune_selectSong(self.obj, song_num)

    def get_info(self, song_num=None):
        """
        Retrieve sub-song specific information. If ``song_num`` is None,
        information about the current active song is returned.

        :param song_num: song number get information
        :type song_num: int or None
        :returns: Information about song
        :rtype: :py:class:`SidTuneInfo`
        """
        if song_num is None:
            info = lib.SidTune_getInfo(self.obj)
        else:
            info = lib.SidTune_getInfoOf(self.obj, song_num)
        if info is None:
            return None
        return SidTuneInfo(info)

    @property
    def status(self):
        """
        Determine current state of object.
        Upon error condition use :py:attr:`status_string` to get a descriptive
        text string."""
        return bool(lib.SidTune_getStatus(self.obj))

    @property
    def status_string(self):
        """Error/status message of last operation."""
        return ffi.string(lib.SidTune_getStatusString(self.obj))

    def create_MD5(self):
        """
        Calculates the MD5 hash of the tune.

        :returns: md5 of this tune
        :rtype: bytes
        """
        md5_str = ffi.new('char[]', self.MD5_LENGTH + 1)
        md5 = lib.SidTune_createMD5(self.obj, md5_str)
        if md5 is None:
            return None
        return bytes(ffi.buffer(md5))

    @property
    def c64_data(self):
        return lib.SidTune_c64Data(self.obj)


class SidClock(Enum):
    UNKNOWN = lib.CLOCK_UNKNOWN
    """Clock unknown"""
    PAL = lib.CLOCK_PAL
    """PAL clock required"""
    NTSC = lib.CLOCK_NTSC
    """NTSC clock required"""
    ANY = lib.CLOCK_ANY
    """Any clock can be used"""


class SidModel(Enum):
    UNKNOWN = lib.SIDMODEL_UNKNOWN
    """SID model unknown."""
    MODEL6581 = lib.SIDMODEL_6581
    """MOS6581 required."""
    MODEL8580 = lib.SIDMODEL_8580
    """MOS8580 required."""
    ANY = lib.SIDMODEL_ANY
    """Any SID model can be used."""


class SidCompatibility(Enum):
    C64 = lib.COMPATIBILITY_C64
    """File is C64 compatible"""
    PSID = lib.COMPATIBILITY_PSID
    """File is PSID specific"""
    R64 = lib.COMPATIBILITY_R64
    """File is Real C64 only"""
    BASIC = lib.COMPATIBILITY_BASIC
    """File requires C64 Basic"""


class SidTuneInfo:
    """
    This interface is used to get values from SidTune objects.

    Create instances of this class by calling :py:func:`SidTune.get_info`.
    """

    def __init__(self, obj):
        self.obj = obj

    _property = _property_builder('SidTuneInfo_songs')

    load_addr = _property('loadAddr', doc='Load Address.')
    init_addr = _property('initAddr', doc='Init Address.')
    play_addr = _property('playAddr', doc='Play Address.')
    songs = _property('songs', doc='The number of songs.')
    start_song = _property('startSong', doc='The default starting song.')
    current_song = _property(
        'currentSong', doc='The tune that has been initialized.')

    def sid_chip_base(self, i):
        """
        The SID chip base address(es) used by the sidtune.

        :param i: chip number
        :type i: int
        :rtype: int
        """
        return lib.SidTuneInfo_sidChipBase(self.obj, i)

    sid_chips = _property(
        'sidChips', doc='Get the number of SID chips required by the tune.')
    song_speed = _property('songSpeed', doc='Intended speed.')
    reloc_start_page = _property(
        'relocStartPage', doc='First available page for relocation.')
    reloc_pages = _property(
        'relocPages', doc='Number of pages available for relocation.')

    def sid_model(self, i):
        """
        The SID chip model(s) requested by the sidtune.

        :param i: chip number
        :type i: int
        :rtype: :py:class:`SidModel`
        """
        return SidModel(lib.SidTuneInfo_sidModel(self.obj, i))

    compatibility = _property(
        'compatibility', result_wrapper=SidCompatibility,
        doc='Compatibility requirements. (see :py:class:`SidCompatibility`)')

    @property
    def info_strings(self):
        """
        Return tune informations: Song title, credits, ...
        - 0 = Title
        - 1 = Author
        - 2 = Released

        :returns: tune information
        :rtype: list
        """
        info_strings = []
        for i in range(lib.SidTuneInfo_numberOfInfoStrings(self.obj)):
            info_string = ffi.string(lib.SidTuneInfo_infoString(self.obj, i))
            info_strings.append(info_string)
        return info_strings

    @property
    def comment_strings(self):
        """
        Tune (MUS) comments.

        :returns: tune information
        :rtype: list
        """
        comment_strings = []
        for i in range(lib.SidTuneInfo_numberOfCommentStrings(self.obj)):
            comment_string = ffi.string(
                lib.SidTuneInfo_commentString(self.obj, i))
            comment_strings.append(comment_string)
        return comment_strings

    data_file_len = _property(
        'dataFileLen', doc='Length of single-file sidtune file.')
    c64data_len = _property(
        'c64dataLen', doc='Length of raw C64 data without load address.')
    clock_speed = _property(
        'clockSpeed', result_wrapper=SidClock,
        doc='The tune clock speed. (see :py:class:`SidClock`)')

    @property
    def format_string(self):
        """The name of the identified file format."""
        return ffi.string(lib.SidTuneInfo_formatString(self.obj))

    fix_load = _property(
        'fixLoad', doc='Whether load address might be duplicate.')

    @property
    def path(self):
        """Path to sidtune files."""
        s = ffi.string(lib.SidTuneInfo_path(self.obj))
        if s == ffi.NULL:
            return None
        return ffi.string(s)

    @property
    def data_filename(self):
        """A first file: e.g. "foo.sid" or "foo.mus"."""
        s = ffi.string(lib.SidTuneInfo_dataFileName(self.obj))
        if s == ffi.NULL:
            return None
        return ffi.string(s)

    @property
    def info_filename(self):
        """A second file: e.g. "foo.str" or None if no second file."""
        s = lib.SidTuneInfo_infoFileName(self.obj)
        if s == ffi.NULL:
            return None
        return ffi.string(s)


class C64Model(Enum):
    """C64 model"""
    PAL = lib.PAL
    "PAL"
    NTSC = lib.NTSC
    "NTSC"
    OLD_NTSC = lib.OLD_NTSC
    "Old NTSC"
    DREAN = lib.DREAN
    "DREAN"


class DefaultSidModel(Enum):
    """Only used internally."""
    MOS6581 = lib.MOS6581
    MOD8580 = lib.MOS8580


class Playback(Enum):
    """Mono or stereo playback."""

    MONO = lib.MONO
    """Mono playback (1 channel)"""
    STEREO = lib.STEREO
    """Stereo playback (2 channels)"""


class SamplingMethod(Enum):
    """Sampling method."""

    INTERPOLATE = lib.INTERPOLATE
    """residfp: ZeroOrderResample"""
    RESAMPLE_INTERPOLATE = lib.RESAMPLE_INTERPOLATE
    """residfp: TwoPassSincResample"""


def _gen_SidConfig_property(name, **kwargs):
    def getter(self):
        func = getattr(lib, 'SidConfig_get_{}'.format(name))
        return func(self.obj)

    def setter(self, value):
        func = getattr(lib, 'SidConfig_set_{}'.format(name))
        return func(self.obj, value)

    return property(getter, setter, **kwargs)


class SidConfig:
    """
    An instance of this class is used to transport emulator settings
    to and from the interface class.
    """

    def __init__(self, obj=None):
        if obj is None:
            obj = lib.SidConfig_new()
            obj = ffi.gc(obj, lib.SidConfig_destroy)
        self.obj = obj

    @property
    def default_c64_model(self):
        """
        Intended c64 model when unknown or forced. (see :py:class:`C64Model`)
        """
        return C64Model(lib.SidConfig_get_defaultC64Model(self.obj))

    @default_c64_model.setter
    def default_c64_model(self, value):
        lib.SidConfig_set_defaultC64Model(self.obj, value.value)

    force_c64_model = _gen_SidConfig_property('forceC64Model', doc='''
        Force the model to :py:attr:`default_c64_model` ignoring tune\'s
        clock setting.''')

    @property
    def default_sid_model(self):
        """
        Intended sid model when unknown or forced. (see :py:class:`SidModel`)
        """
        model = DefaultSidModel(lib.SidConfig_get_defaultSidModell(self.obj))

        if model == DefaultSidModel.MOS6581:
            return SidModel.MODEL6581
        else:
            return SidModel.MODEL8580

    @default_sid_model.setter
    def default_sid_model(self, value):
        sid_model = value.value
        if sid_model == SidModel.MODEL6581:
            sid_model = DefaultSidModel.MOS6581
        elif sid_model == SidModel.MODEL8580:
            sid_model = DefaultSidModel.MOD8580
        else:
            raise ValueError('only MODEL6581 or MODEL8580 allowed')
        lib.SidConfig_set_defaultSidModel(self.obj, sid_model)

    force_sid_model = _gen_SidConfig_property(
        'forceSidModel',
        doc='Force the sid model to :py:attr:`default_sid_model`.')

    @property
    def playback(self):
        """Playbak mode. (see :py:class:`Playback`)"""
        return Playback(lib.SidConfig_get_playback(self.obj))

    @playback.setter
    def playback(self, value):
        lib.SidConfig_set_playback(self.obj, value.value)

    frequency = _gen_SidConfig_property('frequency', doc='Sampling frequency.')

    second_sid_address = _gen_SidConfig_property(
        'secondSidAddress', doc='address of 2nd sid')
    third_sid_address = _gen_SidConfig_property(
        'thirdSidAddress', doc='address of 3rd sid')

    @property
    def sid_emulation(self):
        """
        Selected sid emulation (:py:class:`SidBuilder`)

        Reading this property always returns a :py:class:`SidBuilder`, however
        as this is an abstract class the internal object is actually one of
        :py:class:`ReSIDfpBuilder`, :py:class:`ReSIDBuilder` or
        :py:class:`HardSIDBuilder`.

        Writing to this property supports any of these classes as it is
        casted internally.
        """
        return SidBuilder(lib.SidConfig_get_sidEmulation(self.obj))

    @sid_emulation.setter
    def sid_emulation(self, value):
        builder = ffi.cast('sidbuilder*', value.obj)
        lib.SidConfig_set_sidEmulation(self.obj, builder)

    left_volume = _gen_SidConfig_property(
        'leftVolume', doc='Left channel volume.')

    right_volume = _gen_SidConfig_property(
        'rightVolume', doc='Right channel volume.')

    power_on_delay = _gen_SidConfig_property(
        'powerOnDelay', doc='Power on delay cycles.')

    @property
    def sampling_method(self):
        """Sampling method. (see :py:class:`SamplingMethod`)"""
        return SamplingMethod(lib.SidConfig_get_samplingMethod(self.obj))

    @sampling_method.setter
    def sampling_method(self, value):
        lib.SidConfig_set_samplingMethod(self.obj, value.value)

    fast_sampling = _gen_SidConfig_property(
        'fastSampling', doc='Faster low-quality emulation (only reSID/fp)')


class SidInfo:
    """This provides information about the sid engine implementation."""

    def __init__(self, obj):
        self.obj = obj

    _property = _property_builder('SidInfo_')

    name = _property('name', result_wrapper=ffi.string, doc='Library name')
    version = _property('version', result_wrapper=ffi.string,
                        doc='Library version')

    @property
    def credits(self):
        """Array of library credits"""
        credit_strings = []
        for i in range(lib.SidInfo_numberOfCredits(self.obj)):
            credit_string = ffi.string(lib.SidInfo_credits(self.obj, i))
            credit_strings.append(credit_string)
        return credit_strings

    maxsids = _property(
        'maxsids', doc='Number of SIDs supported by this library')
    channels = _property(
        'channels', doc='Number of output channels (1-mono, 2-stereo)')
    driver_addr = _property('driverAddr', doc='Address of the driver')
    driver_length = _property(
        'driverLength', doc='Size of the driver in bytes')
    power_on_delay = _property('powerOnDelay', doc='Power on delay')

    speed_string = _property(
        'speedString', result_wrapper=ffi.string,
        doc='Describes the speed current song is running at')
    kernal_desc = _property(
        'kernalDesc', result_wrapper=ffi.string,
        doc='Description of the loaded kernal ROM image')
    basic_desc = _property(
        'basicDesc', result_wrapper=ffi.string,
        doc='Description of the loaded basic ROM image')
    chargen_desc = _property(
        'chargenDesc', result_wrapper=ffi.string,
        doc='Description of the loaded character ROM image')


def _SidBuilder_property(name, result_wrapper=None, **kwargs):
    def getter(self):
        func = getattr(lib, 'sidbuilder_{}'.format(name))
        obj = ffi.cast('sidbuilder*', self.obj)
        if result_wrapper is None:
            return func(obj)
        else:
            return result_wrapper(func(obj))

    return property(getter, **kwargs)


class SidBuilder:
    """
    Wrapper for sid builders. Base class of :py:class:`ReSIDfpBuilder`,
    :py:class:`ReSIDBuilder` and :py:class:`HardSIDBuilder`.

    :param obj: sid builder to wrap
    :type obj: ``sidbuilder*``
    """

    def __init__(self, obj):
        self.obj = obj

    _property = _SidBuilder_property

    used_devices = _property('usedDevices', doc='''
        The number of used devices, 0 if none are used.
        ''')
    avail_devices = _property('availDevices', doc='''
        Number of available devices, 0 if  any number is available.''')

    def create(self, sids):
        """
        Create ``sids`` sid emulators.

        :param sids: the number of required sid emulators
        :type sids: int
        :return: number of created sid emulators
        :rtype: int
        """
        obj = ffi.cast('sidbuilder*', self.obj)
        return lib.sidbuilder_create(obj, sids)

    name = _property('name', result_wrapper=ffi.string,
                     doc='The builder\'s name')
    error = _property('error', result_wrapper=ffi.string,
                      doc='current error message')
    status = _property('getStatus', result_wrapper=bool, doc='''
        current error status: True if no error occured, False otherwise''')
    credits = _property('credits', result_wrapper=ffi.string, doc='''
        credits of this sid builder.''')

    def filter(self, enable):
        """
        Toggle sid filter emulation.

        :param enable: Enable of disable filter emulation
        :type enable: bool
        """
        obj = ffi.cast('sidbuilder*', self.obj)
        lib.sidbuilder_filter(obj, enable)


class ReSIDfpBuilder(SidBuilder):
    """ReSIDfp Builder Class"""

    def __init__(self, name_or_obj_or_sidbuilder):
        if isinstance(name_or_obj_or_sidbuilder, str):
            name = name_or_obj_or_sidbuilder
            b_name = name.encode('utf-8')
            obj = lib.ReSIDfpBuilder_new(b_name)
        elif isinstance(name_or_obj_or_sidbuilder, SidBuilder):
            obj = ffi.cast('ReSIDfpBuilder*', name_or_obj_or_sidbuilder.obj)
        else:
            obj = name_or_obj_or_sidbuilder
        obj = ffi.gc(obj, lib.ReSIDfpBuilder_destroy)
        super().__init__(obj)

    def filter_6581_curve(self, filter_curve):
        """
        Set 6581 filter curve.

        :param filter_curve: filterCurve from 0.0 (light) to
            1.0 (dark) (default 0.5)
        :type filter_curve: double
        """
        lib.ReSIDfpBuilder_filter6581Curve(self.obj, filter_curve)

    def filter_8580_curve(self, filter_curve):
        """
        Set 8580 filter curve.

        :param filter_curve: curve center frequency (default 12500)
        :type filter_curve: double
        """
        lib.ReSIDfpBuilder_filter8580Curve(self.obj, filter_curve)


class ReSIDBuilder(SidBuilder):
    """ReSID Builder Class"""

    def __init__(self, name_or_obj_or_sidbuilder):
        if isinstance(name_or_obj_or_sidbuilder, str):
            name = name_or_obj_or_sidbuilder
            b_name = name.encode('utf-8')
            obj = lib.ReSIDBuilder_new(b_name)
        elif isinstance(name_or_obj_or_sidbuilder, SidBuilder):
            obj = ffi.cast('ReSIDBuilder*', name_or_obj_or_sidbuilder.obj)
        else:
            obj = name_or_obj_or_sidbuilder
        obj = ffi.gc(obj, lib.ReSIDBuilder_destroy)
        super().__init__(obj)

    def bias(self, dac_bias):
        """
        The bias is given in millivolts, and a maximum reasonable
        control range is approximately -500 to 500.
        """
        lib.ReSIDBuilder_bias(self.obj, dac_bias)


class HardSIDBuilder(SidBuilder):
    """HardSID Builder Class"""

    def __init__(self, name_or_obj_or_sidbuilder):
        if isinstance(name_or_obj_or_sidbuilder, str):
            name = name_or_obj_or_sidbuilder
            b_name = name.encode('utf-8')
            obj = lib.HardSIDBuilder_new(b_name)
        elif isinstance(name_or_obj_or_sidbuilder, SidBuilder):
            obj = ffi.cast('HardSIDBuilder*', name_or_obj_or_sidbuilder.obj)
        else:
            obj = name_or_obj_or_sidbuilder
        obj = ffi.gc(obj, lib.HardSIDBuilder_destroy)
        super().__init__(obj)


class SidDatabaseError(SidPlayfpError):
    """Exception raised by :py:class:`SidDatabase`"""
    pass


class SidDatabase:
    """An utility class to deal with the songlength database."""

    def __init__(self):
        obj = lib.SidDatabase_new()
        self.obj = ffi.gc(obj, lib.SidDatabase_destroy)

    def open(self, filename):
        """
        Open the songlength DataBase.

        :param filename: full path to songlength db
        :raises SidDatabaseError: if songlength db could not be loaded
        """
        opened = lib.SidDatabase_open(self.obj, bytes(filename))

        if not opened:
            raise self._raise_error()

    def close(self):
        """Close the songlength database."""
        lib.SidDatabase_close(self.obj)

    def length(self, tune_or_md5, song_num=None):
        """
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
        """
        if song_num is not None:
            md5 = bytes(tune_or_md5)
            length = lib.SidDatabase_length_md5(self.obj, md5, song_num)
        else:
            tune = tune_or_md5
            length = lib.SidDatabase_length_tune(self.obj, tune.obj)

        if length == -1:
            raise self._raise_error()

        return length

    @property
    def error(self):
        """Get descriptive error message."""
        return ffi.string(lib.SidDatabase_error(self.obj))

    def _raise_error(self):
        raise SidDatabaseError(self.err)
