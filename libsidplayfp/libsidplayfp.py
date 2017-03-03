#!/usr/bin/env python3
import os
from enum import Enum

from libsidplayfp._libsidplayfp import ffi, lib


def _property_builder(prefix):
    def generate_property(name, result_wrapper=None, **kwargs):
        def getter(self):
            func = getattr(lib, '{}{}'.format(prefix, name))
            if result_wrapper is None:
                return func(self.obj)
            else:
                return result_wrapper(func(self.obj))

        return property(getter, **kwargs)

    return generate_property


class SIDPlayfp:

    def __init__(self):
        obj = lib.sidplayfp_new()
        self.obj = ffi.gc(obj, lib.sidplayfp_destroy)

    @property
    def config(self):
        return SidConfig(lib.sidplayfp_getConfig(self.obj))

    @config.setter
    def config(self, config):
        lib.sidplayfp_setConfig(self.obj, config.obj)

    @property
    def info(self):
        return SidInfo(lib.sidplayfp_info(self.obj))

    @property
    def error(self):
        return ffi.string(lib.sidplayfp_error(self.obj))

    def fast_forward(self, percent):
        return lib.sidplayfp_fastForward(self.obj, percent)

    def load(self, tune):
        return lib.sidplayfp_load(self.obj, tune.obj)

    def play(self, buffer):
        buf = ffi.from_buffer(buffer)
        buf = ffi.cast('short*', buf)
        buf_len = len(buffer) // 2  # 2 byte = 1 short
        return lib.sidplayfp_play(self.obj, buf, buf_len)

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

    def __repr__(self):
        return repr(self.obj)


class SidTune:

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
        sep_is_slash = os.sep == '/'
        lib.SidTune_load(self.obj, filename, sep_is_slash)

    def read(self, source_buffer):
        lib.SidTune_read(
            self.obj, ffi.from_buffer(source_buffer), len(source_buffer))

    def select_song(self, song_num):
        return lib.SidTune_selectSong(self.obj, song_num)

    def get_info(self, song_num=None):
        if song_num is None:
            info = lib.SidTune_getInfo(self.obj)
        else:
            info = lib.SidTune_getInfoOf(self.obj, song_num)
        return SidTuneInfo(info)

    @property
    def status(self):
        return lib.SidTune_getStatus(self.obj)

    @property
    def status_string(self):
        return ffi.string(lib.SidTune_getStatusString(self.obj))

    def create_MD5(self):
        md5_str = ffi.new('char[]', self.MD5_LENGTH + 1)
        md5 = lib.SidTune_createMD5(self.obj, md5_str)
        if md5 is None:
            return None
        return ffi.string(md5)

    @property
    def c64_data(self):
        return lib.SidTune_c64Data(self.obj)


class SidClock(Enum):
    UNKNOWN = lib.CLOCK_UNKNOWN
    PAL = lib.CLOCK_PAL
    NTSC = lib.CLOCK_NTSC
    ANY = lib.CLOCK_ANY


class SidModel(Enum):
    UNKNOWN = lib.SIDMODEL_UNKNOWN
    MODEL6581 = lib.SIDMODEL_6581
    MODEL8580 = lib.SIDMODEL_8580
    ANY = lib.SIDMODEL_ANY


class SidCompatibility(Enum):
    C64 = lib.COMPATIBILITY_C64
    PSID = lib.COMPATIBILITY_PSID
    R64 = lib.COMPATIBILITY_R64
    BASIC = lib.COMPATIBILITY_BASIC


class SidTuneInfo:

    def __init__(self, obj):
        self.obj = obj

    _property = _property_builder('SidTuneInfo_songs')

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

    compatibility = _property('compatibility')

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
    clock_speed = _property('clockSpeed')

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
    PAL = lib.PAL
    NTSC = lib.NTSC
    OLD_NTSC = lib.OLD_NTSC
    DREAN = lib.DREAN


class DefaultSidModel(Enum):
    MOS6581 = lib.MOS6581
    MOD8580 = lib.MOS8580


class Playback(Enum):
    MONO = lib.MONO
    STEREO = lib.STEREO


class SamplingMethod(Enum):
    INTERPOLATE = lib.INTERPOLATE
    RESAMPLE_INTERPOLATE = lib.RESAMPLE_INTERPOLATE


def _gen_SidConfig_property(name, **kwargs):
    def getter(self):
        func = getattr(lib, 'SidConfig_get_{}'.format(name))
        return func(self.obj)

    def setter(self, value):
        func = getattr(lib, 'SidConfig_set_{}'.format(name))
        return func(self.obj, value)

    return property(getter, setter, **kwargs)


class SidConfig:

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
        return DefaultSidModel(lib.SidConfig_get_defaultSidModell(self.obj))

    @default_sid_model.setter
    def default_sid_model(self, value):
        lib.SidConfig_set_defaultSidModel(self.obj, value.value)

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


# def _gen_SidInfo_default_property(name, **kwargs):
#     def getter(self):
#         func = getattr(lib, 'SidInfo_{}'.format(name))
#         return func(self.obj)

#     return property(getter, **kwargs)


# def _gen_SidInfo_str_property(name, **kwargs):
#     def getter(self):
#         func = getattr(lib, 'SidInfo_{}'.format(name))
#         return ffi.string(func(self.obj))

#     return property(getter, **kwargs)

# old:
    # name = _gen_SidInfo_str_property('name')
    # version = _gen_SidInfo_str_property('version')

    # @property
    # def credits(self):
    #     credit_strings = []
    #     for i in range(lib.SidInfo_numberOfCredits(self.obj)):
    #         credit_string = ffi.string(lib.SidInfo_credits(self.obj, i))
    #         credit_strings.append(credit_string)
    #     return credit_strings

    # maxsids = _gen_SidInfo_default_property('maxsids')
    # channels = _gen_SidInfo_default_property('channels')
    # driver_addr = _gen_SidInfo_default_property('driverAddr')
    # driver_length = _gen_SidInfo_default_property('driverLength')
    # power_on_delay = _gen_SidInfo_default_property('powerOnDelay')

    # speed_string = _gen_SidInfo_str_property('speedString')
    # kernal_desc = _gen_SidInfo_str_property('kernalDesc')
    # basic_desc = _gen_SidInfo_str_property('basicDesc')
    # chargen_desc = _gen_SidInfo_str_property('chargenDesc')


class SidInfo:

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


# def _gen_SidBuilder_default_property(name, **kwargs):
#     def getter(self):
#         func = getattr(lib, 'sidbuilder_{}'.format(name))
#         obj = ffi.cast('sidbuilder*', self.obj)
#         return func(obj)

#     return property(getter, **kwargs)


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
    status = _property('getStatus')
    credits = _property('credits', result_wrapper=ffi.string)

    def filter(self, enable):
        obj = ffi.cast('sidbuilder*', self.obj)
        lib.sidbuilder_filter(obj, enable)


class ReSIDfpBuilder(SidBuilder):

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
        lib.ReSIDfpBuilder_filter6581Curve(self.obj, filter_curve)

    def filter_8580_curve(self, filter_curve):
        lib.ReSIDfpBuilder_filter8580Curve(self.obj, filter_curve)


class ReSIDBuilder(SidBuilder):

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
        lib.ReSIDBuilder_bias(self.obj, dac_bias)


class HardSIDBuilder(SidBuilder):

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
