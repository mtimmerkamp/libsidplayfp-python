#!/usr/bin/env python3
# This file is part of libsidplyfp(-python), a Python wrapper to
# libsidplayfp, a SID player engine.

# Copyright (C) 2017 Maximilian Timmerkamp
# Many parts of the wrapper classes' documentation is directly from
# libsidplayfp. So the respective authors of libsidplayfp hold the
# copyright on these parts of the documentation.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
from enum import Enum

from libsidplayfp._libsidplayfp import ffi, lib


class SidError(Exception):
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


class SidPlayfpConfigError(SidError):
    """Error raised while setting :py:attr:`SidPlayfp.config`."""
    pass


class SidPlayfpLoadError(SidError):
    """Error raised by :py:func:`SidPlayfp.load` while loading a tune."""
    pass


class SidPlayfp:
    """Main interface to libsidplayfp to play tunes."""

    def __init__(self):
        obj = lib.sidplayfp_new()
        self.obj = ffi.gc(obj, lib.sidplayfp_destroy)

        # store current tune to prevent SIGSEGVs when calling stop()
        self._current_tune = None

        self._config = None

    @property
    def config(self):
        if self._config is None:
            self._config = SidConfig(lib.sidplayfp_getConfig(self.obj))
        return self._config

    @config.setter
    def config(self, config):
        self._config = config

    def configure(self):
        success = lib.sidplayfp_setConfig(self.obj, self.config.obj)

        if not success:
            raise SidPlayfpConfigError(self.error)

    @property
    def info(self):
        return SidInfo(lib.sidplayfp_info(self.obj))

    @property
    def error(self):
        return ffi.string(lib.sidplayfp_error(self.obj))

    def fast_forward(self, percent):
        return lib.sidplayfp_fastForward(self.obj, percent)

    def load(self, tune):
        success = lib.sidplayfp_load(self.obj, tune.obj)

        if not success:
            raise SidPlayfpLoadError(self.error)

        self._current_tune = tune

    def play(self, buffer, length=None):
        buf = ffi.from_buffer(buffer)
        buf = ffi.cast('short*', buf)
        if length is None:
            length = len(buffer) // 2  # 2 byte = 1 short
        return lib.sidplayfp_play(self.obj, buf, length)

    @property
    def is_playing(self):
        return lib.sidplayfp_isPlaying(self.obj)

    def stop(self):
        lib.sidplayfp_stop(self.obj)

    def debug(self, enable, file_=None):
        lib.sidplayfp_debug(self.obj, enable, file_)

    def mute(self, sid_num, voice, enable):
        lib.sidplayfp_mute(self.obj, sid_num, voice, enable)

    @property
    def time(self):
        return lib.sidplayfp_time(self.obj)

    def set_roms(self, kernal, basic=None, character=None):
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
        return lib.sidplayfp_getCia1TimerA(self.obj)


class SidTuneError(SidError):
    """Error raised when loading or reading a :py:class:`SidTune` fails."""
    pass


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

    """

    MD5_LENGTH = lib.MD5_LENGTH

    def __init__(self, filename=None, source_buffer=None):
        if source_buffer is not None:
            obj = lib.SidTune_new_from_buffer(
                ffi.from_buffer(source_buffer), len(source_buffer))
        elif filename is None:
            raise ValueError(
                'either filename or source_buffer must not be None')
        else:
            filename_exts = ffi.cast('char**', 0)
            sep_is_slash = os.sep == '/'

            obj = lib.SidTune_new_from_filename(
                filename, filename_exts, sep_is_slash)

        self.obj = ffi.gc(obj, lib.SidTune_destroy)

        if not self.status:
            raise SidTuneError(self.status_string)

    def load(self, filename):
        sep_is_slash = os.sep == '/'
        lib.SidTune_load(self.obj, filename, sep_is_slash)

        if not self.status:
            raise SidTuneError(self.status_string)

    def read(self, source_buffer):
        lib.SidTune_read(
            self.obj, ffi.from_buffer(source_buffer), len(source_buffer))

        if not self.status:
            raise SidTuneError(self.status_string)

    def select_song(self, song_num):
        return lib.SidTune_selectSong(self.obj, song_num)

    def get_info(self, song_num=None):
        if song_num is None:
            info = lib.SidTune_getInfo(self.obj)
        else:
            info = lib.SidTune_getInfoOf(self.obj, song_num)
        if info is None:
            return None
        return SidTuneInfo(info)

    @property
    def status(self):
        return bool(lib.SidTune_getStatus(self.obj))

    @property
    def status_string(self):
        return ffi.string(lib.SidTune_statusString(self.obj))

    def create_MD5(self):
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

    _property = _property_builder('SidTuneInfo_')

    load_addr = _property('loadAddr')
    init_addr = _property('initAddr')
    play_addr = _property('playAddr')
    songs = _property('songs')
    start_song = _property('startSong')
    current_song = _property('currentSong')

    def sid_chip_base(self, i):
        return lib.SidTuneInfo_sidChipBase(self.obj, i)

    sid_chips = _property('sidChips')
    song_speed = _property('songSpeed')
    reloc_start_page = _property('relocStartPage')
    reloc_pages = _property('relocPages')

    def sid_model(self, i):
        return SidModel(lib.SidTuneInfo_sidModel(self.obj, i))

    compatibility = _property('compatibility', result_wrapper=SidCompatibility)

    @property
    def info_strings(self):
        info_strings = []
        for i in range(lib.SidTuneInfo_numberOfInfoStrings(self.obj)):
            info_string = ffi.string(lib.SidTuneInfo_infoString(self.obj, i))
            info_strings.append(info_string)
        return info_strings

    @property
    def comment_strings(self):
        comment_strings = []
        for i in range(lib.SidTuneInfo_numberOfCommentStrings(self.obj)):
            comment_string = ffi.string(
                lib.SidTuneInfo_commentString(self.obj, i))
            comment_strings.append(comment_string)
        return comment_strings

    data_file_len = _property('dataFileLen')
    c64data_len = _property('c64dataLen')
    clock_speed = _property('clockSpeed', result_wrapper=SidClock)

    @property
    def format_string(self):
        return ffi.string(lib.SidTuneInfo_formatString(self.obj))

    fix_load = _property('fixLoad')

    @property
    def path(self):
        s = ffi.string(lib.SidTuneInfo_path(self.obj))
        if s == ffi.NULL:
            return None
        return ffi.string(s)

    @property
    def data_filename(self):
        s = ffi.string(lib.SidTuneInfo_dataFileName(self.obj))
        if s == ffi.NULL:
            return None
        return ffi.string(s)

    @property
    def info_filename(self):
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
    to and from the interface class. Writing to any property is allowed
    (and necessary to configure the engine).
    """

    def __init__(self, obj=None):
        if obj is None:
            obj = lib.SidConfig_new()
            obj = ffi.gc(obj, lib.SidConfig_destroy)
        self.obj = obj

    @property
    def default_c64_model(self):
        return C64Model(lib.SidConfig_get_defaultC64Model(self.obj))

    @default_c64_model.setter
    def default_c64_model(self, value):
        lib.SidConfig_set_defaultC64Model(self.obj, value.value)

    force_c64_model = _gen_SidConfig_property('forceC64Model')

    @property
    def default_sid_model(self):
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

    force_sid_model = _gen_SidConfig_property('forceSidModel')

    @property
    def playback(self):
        return Playback(lib.SidConfig_get_playback(self.obj))

    @playback.setter
    def playback(self, value):
        lib.SidConfig_set_playback(self.obj, value.value)

    frequency = _gen_SidConfig_property('frequency')

    second_sid_address = _gen_SidConfig_property('secondSidAddress')
    third_sid_address = _gen_SidConfig_property('thirdSidAddress')

    @property
    def sid_emulation(self):
        return SidBuilder(lib.SidConfig_get_sidEmulation(self.obj))

    @sid_emulation.setter
    def sid_emulation(self, value):
        builder = ffi.cast('sidbuilder*', value.obj)
        lib.SidConfig_set_sidEmulation(self.obj, builder)

    left_volume = _gen_SidConfig_property('leftVolume')

    right_volume = _gen_SidConfig_property('rightVolume')

    power_on_delay = _gen_SidConfig_property('powerOnDelay')

    @property
    def sampling_method(self):
        return SamplingMethod(lib.SidConfig_get_samplingMethod(self.obj))

    @sampling_method.setter
    def sampling_method(self, value):
        lib.SidConfig_set_samplingMethod(self.obj, value.value)

    fast_sampling = _gen_SidConfig_property('fastSampling')


class SidInfo:
    """This provides information about the sid engine implementation."""

    def __init__(self, obj):
        self.obj = obj

    _property = _property_builder('SidInfo_')

    name = _property('name', result_wrapper=ffi.string)
    version = _property('version', result_wrapper=ffi.string)

    @property
    def credits(self):
        credit_strings = []
        for i in range(lib.SidInfo_numberOfCredits(self.obj)):
            credit_string = ffi.string(lib.SidInfo_credits(self.obj, i))
            credit_strings.append(credit_string)
        return credit_strings

    maxsids = _property('maxsids')
    channels = _property('channels')
    driver_addr = _property('driverAddr')
    driver_length = _property('driverLength')
    power_on_delay = _property('powerOnDelay')

    speed_string = _property('speedString', result_wrapper=ffi.string)
    kernal_desc = _property('kernalDesc', result_wrapper=ffi.string)
    basic_desc = _property('basicDesc', result_wrapper=ffi.string)
    chargen_desc = _property('chargenDesc', result_wrapper=ffi.string)


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
    Wrapper for sid builders.

    libsidplayfp offers two additional methods
    ``sidemu *lock(EventContext *env, SidConfig::sid_model_t model);`` and
    ``void unlock(sidemu *device);`` which are not offered by this wrapper
    class. These functions are intended for internal use to provide
    the player with the required SID chips even though they are part of
    ``sidbuilder``'s public interface.
    """

    def __init__(self, obj):
        self.obj = obj

    _property = _SidBuilder_property

    used_devices = _property('usedDevices')
    avail_devices = _property('availDevices')

    def create(self, sids):
        obj = ffi.cast('sidbuilder*', self.obj)
        return lib.sidbuilder_create(obj, sids)

    name = _property('name', result_wrapper=ffi.string)
    error = _property('error', result_wrapper=ffi.string)
    status = _property('getStatus', result_wrapper=bool)
    credits = _property('credits', result_wrapper=ffi.string)

    def filter(self, enable):
        obj = ffi.cast('sidbuilder*', self.obj)
        lib.sidbuilder_filter(obj, enable)


class ReSIDfpBuilder(SidBuilder):
    """
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
    """

    def __init__(self, name=None, cast=None, cdata=None):
        if name is not None:
            b_name = name.encode('utf-8')
            obj = lib.ReSIDfpBuilder_new(b_name)
            obj = ffi.gc(obj, lib.ReSIDfpBuilder_destroy)
        elif cast is not None:
            obj = ffi.cast('ReSIDfpBuilder*', cast.obj)
        else:
            obj = ffi.cast('ReSIDfpBuilder*', cdata)
        super().__init__(obj)

    def filter_6581_curve(self, filter_curve):
        lib.ReSIDfpBuilder_filter6581Curve(self.obj, filter_curve)

    def filter_8580_curve(self, filter_curve):
        lib.ReSIDfpBuilder_filter8580Curve(self.obj, filter_curve)


class ReSIDBuilder(SidBuilder):
    """
    ReSID Builder Class

    For an explanation on the parameter see :py:class:`ReSIDfpBuilder`.
    """

    def __init__(self, name=None, cast=None, cdata=None):
        if name is not None:
            b_name = name.encode('utf-8')
            obj = lib.ReSIDBuilder_new(b_name)
            obj = ffi.gc(obj, lib.ReSIDBuilder_destroy)
        elif cast is not None:
            obj = ffi.cast('ReSIDBuilder*', cast.obj)
        else:
            obj = ffi.cast('ReSIDBuilder*', cdata)
        super().__init__(obj)

    def bias(self, dac_bias):
        lib.ReSIDBuilder_bias(self.obj, dac_bias)


class HardSIDBuilder(SidBuilder):
    """
    HardSID Builder Class

    For an explanation on the parameter see :py:class:`ReSIDfpBuilder`.
    """

    def __init__(self, name=None, cast=None, cdata=None):
        if name is not None:
            b_name = name.encode('utf-8')
            obj = lib.HardSIDBuilder_new(b_name)
            obj = ffi.gc(obj, lib.HardSIDBuilder_destroy)
        elif cast is not None:
            obj = ffi.cast('HardSIDBuilder*', cast.obj)
        else:
            obj = ffi.cast('HardSIDBuilder*', cdata)
        super().__init__(obj)


class SidDatabaseError(SidError):
    """Exception raised by :py:class:`SidDatabase`"""
    pass


class SidDatabase:
    """An utility class to deal with the songlength database."""

    def __init__(self):
        obj = lib.SidDatabase_new()
        self.obj = ffi.gc(obj, lib.SidDatabase_destroy)

    def open(self, filename):
        opened = lib.SidDatabase_open(self.obj, bytes(filename))

        if not opened:
            raise self._raise_error()

    def close(self):
        lib.SidDatabase_close(self.obj)

    def length(self, tune_or_md5, song_num=None):
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
        return ffi.string(lib.SidDatabase_error(self.obj))

    def _raise_error(self):
        raise SidDatabaseError(self.err)
