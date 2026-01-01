/* This file is part of libsidplyfp(-python), a Python wrapper to
 * libsidplayfp, a SID player engine.
 *
 * Copyright (C) 2017 Maximilian Timmerkamp
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

typedef struct sidplayfp sidplayfp;
typedef struct SidConfig SidConfig;
typedef struct SidInfo SidInfo;
typedef struct SidTune SidTune;
typedef struct SidTuneInfo SidTuneInfo;
typedef struct sidbuilder sidbuilder;
typedef struct ReSIDfpBuilder ReSIDfpBuilder;
typedef struct ReSIDBuilder ReSIDBuilder;
typedef struct HardSIDBuilder HardSIDBuilder;
typedef struct SidDatabase SidDatabase;


// sidplayfp (interface to Player)

sidplayfp* sidplayfp_new();
void sidplayfp_destroy(sidplayfp* self);
const SidConfig* sidplayfp_getConfig(sidplayfp* self);
const SidInfo* sidplayfp_info(sidplayfp* self);
bool sidplayfp_setConfig(sidplayfp* self, const SidConfig* cfg);
const char* sidplayfp_error(sidplayfp* self);
bool sidplayfp_fastForward(sidplayfp* self, unsigned int percent);
bool sidplayfp_load(sidplayfp* self, SidTune *tune);
uint_least32_t sidplayfp_play(sidplayfp* self, short *buffer,
    uint_least32_t count);
bool sidplayfp_isPlaying(sidplayfp* self);
void sidplayfp_stop(sidplayfp* self);
void sidplayfp_debug(sidplayfp* self, bool enable, FILE* out);
void sidplayfp_mute(sidplayfp* self, unsigned int sidNum, unsigned int voice,
    bool enable);
uint_least32_t sidplayfp_time(sidplayfp* self);
void sidplayfp_setRoms(sidplayfp* self, const uint8_t* kernal,
    const uint8_t* basic, const uint8_t* character);
uint_least16_t sidplayfp_getCia1TimerA(sidplayfp* self);


// SidTune
static const int MD5_LENGTH;

SidTune* SidTune_new_from_filename(const char* fileName,
    const char** fileNameExt, bool separatorIsSlash);
SidTune* SidTune_new_from_buffer(const uint_least8_t* oneFileFormatSidtune,
    uint_least32_t sidtuneLength);
void SidTune_destroy(SidTune* self);
void SidTune_setFileNameExtensions(SidTune* self, const char **fileNameExt);
void SidTune_load(SidTune* self, const char* fileName, bool separatorIsSlash);
void SidTune_read(SidTune* self, const uint_least8_t* sourceBuffer,
    uint_least32_t bufferLen);
unsigned int SidTune_selectSong(SidTune* self, unsigned int songNum);
const SidTuneInfo* SidTune_getInfo(SidTune* self);
const SidTuneInfo* SidTune_getInfoOf(SidTune* self, unsigned int songNum);
bool SidTune_getStatus(SidTune* self);
const char* SidTune_statusString(SidTune* self);
// bool SidTune_placeSidTuneInC64mem(SidTune* self, sidmemory* mem);
const char* SidTune_createMD5(SidTune* self, char *md5);
const uint_least8_t* SidTune_c64Data(SidTune* self);


// SidTuneInfo
typedef enum {CLOCK_UNKNOWN, CLOCK_PAL, CLOCK_NTSC, CLOCK_ANY, ...}
    sid_clock_t;
typedef enum {SIDMODEL_UNKNOWN, SIDMODEL_6581, SIDMODEL_8580,
    SIDMODEL_ANY, ...} sid_model_t;
typedef enum {COMPATIBILITY_C64, COMPATIBILITY_PSID, COMPATIBILITY_R64,
    COMPATIBILITY_BASIC, ...} sid_compatibility_t;

uint_least16_t SidTuneInfo_loadAddr(SidTuneInfo* self);
uint_least16_t SidTuneInfo_initAddr(SidTuneInfo* self);
uint_least16_t SidTuneInfo_playAddr(SidTuneInfo* self);

unsigned int SidTuneInfo_songs(SidTuneInfo* self);
unsigned int SidTuneInfo_startSong(SidTuneInfo* self);
unsigned int SidTuneInfo_currentSong(SidTuneInfo* self);

uint_least16_t SidTuneInfo_sidChipBase(SidTuneInfo* self, unsigned int i);
int SidTuneInfo_sidChips(SidTuneInfo* self);
int SidTuneInfo_songSpeed(SidTuneInfo* self);

uint_least8_t SidTuneInfo_relocStartPage(SidTuneInfo* self);
uint_least8_t SidTuneInfo_relocPages(SidTuneInfo* self);

sid_model_t SidTuneInfo_sidModel(SidTuneInfo* self, unsigned int i);
sid_compatibility_t SidTuneInfo_compatibility(SidTuneInfo* self);

unsigned int SidTuneInfo_numberOfInfoStrings(SidTuneInfo* self);
const char* SidTuneInfo_infoString(SidTuneInfo* self, unsigned int i);

unsigned int SidTuneInfo_numberOfCommentStrings(SidTuneInfo* self);
const char* SidTuneInfo_commentString(SidTuneInfo* self, unsigned int i);

uint_least32_t SidTuneInfo_dataFileLen(SidTuneInfo* self);
uint_least32_t SidTuneInfo_c64dataLen(SidTuneInfo* self);
sid_clock_t SidTuneInfo_clockSpeed(SidTuneInfo* self);
const char* SidTuneInfo_formatString(SidTuneInfo* self);
bool SidTuneInfo_fixLoad(SidTuneInfo* self);

const char* SidTuneInfo_path(SidTuneInfo* self);
const char* SidTuneInfo_dataFileName(SidTuneInfo* self);
const char* SidTuneInfo_infoFileName(SidTuneInfo* self);


// SidConfig
typedef enum {MONO = 1,  STEREO} playback_t;
typedef enum {MOS6581, MOS8580} default_sid_model_t;
typedef enum {PAL, NTSC, OLD_NTSC, DREAN} c64_model_t;
typedef enum {INTERPOLATE, RESAMPLE_INTERPOLATE} sampling_method_t;

SidConfig* SidConfig_new();
void SidConfig_destroy(SidConfig* self);

c64_model_t SidConfig_get_defaultC64Model(SidConfig* self);
void SidConfig_set_defaultC64Model(SidConfig* self, c64_model_t value);

bool SidConfig_get_forceC64Model(SidConfig* self);
void SidConfig_set_forceC64Model(SidConfig* self, bool value);

sid_model_t SidConfig_get_defaultSidModel(SidConfig* self);
void SidConfig_set_defaultSidModel(SidConfig* self, sid_model_t value);

bool SidConfig_get_forceSidModel(SidConfig* self);
void SidConfig_set_forceSidModel(SidConfig* self, bool value);

playback_t SidConfig_get_playback(SidConfig* self);
void SidConfig_set_playback(SidConfig* self, playback_t value);

uint_least32_t SidConfig_get_frequency(SidConfig* self);
void SidConfig_set_frequency(SidConfig* self, uint_least32_t value);

uint_least16_t SidConfig_get_secondSidAddress(SidConfig* self);
void SidConfig_set_secondSidAddress(SidConfig* self, uint_least16_t value);
uint_least16_t SidConfig_get_thirdSidAddress(SidConfig* self);
void SidConfig_set_thirdSidAddress(SidConfig* self, uint_least16_t value);

sidbuilder* SidConfig_get_sidEmulation(SidConfig* self);
void SidConfig_set_sidEmulation(SidConfig* self, sidbuilder* value);

uint_least32_t SidConfig_get_leftVolume(SidConfig* self);
void SidConfig_set_leftVolume(SidConfig* self, uint_least32_t value);

uint_least32_t SidConfig_get_rightVolume(SidConfig* self);
void SidConfig_set_rightVolume(SidConfig* self, uint_least32_t value);

uint_least16_t SidConfig_get_powerOnDelay(SidConfig* self);
void SidConfig_set_powerOnDelay(SidConfig* self, uint_least16_t value);

sampling_method_t SidConfig_get_samplingMethod(SidConfig* self);
void SidConfig_set_samplingMethod(SidConfig* self, sampling_method_t value);

bool SidConfig_get_fastSampling(SidConfig* self);
void SidConfig_set_fastSampling(SidConfig* self, bool value);


// SidInfo
const char* SidInfo_name(SidInfo* self);
const char* SidInfo_version(SidInfo* self);
unsigned int SidInfo_numberOfCredits(SidInfo* self);
const char* SidInfo_credits(SidInfo* self, unsigned int i);
unsigned int SidInfo_maxsids(SidInfo* self);
unsigned int SidInfo_channels(SidInfo* self);
uint_least16_t SidInfo_driverAddr(SidInfo* self);
uint_least16_t SidInfo_driverLength(SidInfo* self);
uint_least16_t SidInfo_powerOnDelay(SidInfo* self);
const char* SidInfo_speedString(SidInfo* self);
const char* SidInfo_kernalDesc(SidInfo* self);
const char* SidInfo_basicDesc(SidInfo* self);
const char* SidInfo_chargenDesc(SidInfo* self);


// sidbuilder
void sidbuilder_destroy(sidbuilder* self);
unsigned int sidbuilder_usedDevices(sidbuilder* self);
unsigned int sidbuilder_availDevices(sidbuilder* self);
unsigned int sidbuilder_create(sidbuilder* self, unsigned int sids);
const char* sidbuilder_name(sidbuilder* self);
const char* sidbuilder_error(sidbuilder* self);
bool sidbuilder_getStatus(sidbuilder* self);
const char* sidbuilder_credits(sidbuilder* self);
void sidbuilder_filter(sidbuilder* self, bool enable);


// ReSIDfpBuilder
ReSIDfpBuilder* ReSIDfpBuilder_new(const char * name);
void ReSIDfpBuilder_destroy(ReSIDfpBuilder* self);
//unsigned int ReSIDfpBuilder_availDevices(ReSIDfpBuilder* self);
//unsigned int ReSIDfpBuilder_create(ReSIDfpBuilder* self, unsigned int sids);
//const char* ReSIDfpBuilder_credits(ReSIDfpBuilder* self);
//void ReSIDfpBuilder_filter(ReSIDfpBuilder* self, bool enable);
void ReSIDfpBuilder_filter6581Curve(ReSIDfpBuilder* self, double filterCurve);
void ReSIDfpBuilder_filter8580Curve(ReSIDfpBuilder* self, double filterCurve);
/* unsigned int ReSIDfpBuilder_usedDevices(ReSIDfpBuilder* self);
 const char* ReSIDfpBuilder_name(ReSIDfpBuilder* self);
 const char* ReSIDfpBuilder_error(ReSIDfpBuilder* self);
 bool ReSIDfpBuilder_getStatus(ReSIDfpBuilder* self); */


// ReSIDBuilder
ReSIDBuilder* ReSIDBuilder_new(const char* name);
void ReSIDBuilder_destroy(ReSIDBuilder* self);
void ReSIDBuilder_bias(ReSIDBuilder* self, double dac_bias);


// SidDatabase
SidDatabase* SidDatabase_new();
void SidDatabase_destroy(SidDatabase* self);
bool SidDatabase_open(SidDatabase* self, const char *filename);
void SidDatabase_close(SidDatabase* self);
int_least32_t SidDatabase_length_tune(SidDatabase* self, SidTune* tune);
int_least32_t SidDatabase_length_md5(SidDatabase* self,
    const char *md5, unsigned int song);
const char* SidDatabase_error(SidDatabase* self);
