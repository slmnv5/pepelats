from math import log10

import numpy as np
import sounddevice as sd

from utils.utilconfig import load_ini_section, ConfigName, SD_RATE
from utils.utillog import MYLOG


def make_buffer(sz: int) -> np.ndarray:
    return np.zeros((sz, AUDIO_INFO.SD_CH), AUDIO_INFO.SD_TYPE)


def correct_sound(x: np.ndarray, channels: int, datatype: str) -> np.ndarray:
    """ Convert numpy array to given channels and datatype """
    assert x.ndim in [1, 2]
    assert channels in [1, 2]
    if x.ndim == 1:
        MYLOG.error(f"Re-shaping one dimensional array, shape: {x.shape}")
        x = x.reshape(-1, 1)
    if x.dtype != AUDIO_INFO.SD_TYPE:
        MYLOG.warning(f"Correcting array type: {x.dtype} to {AUDIO_INFO.SD_TYPE}")
        factor = get_conversion_factor(x.dtype, datatype)
        x = (x * factor).astype(datatype)

    if x.shape[1] != AUDIO_INFO.SD_CH:
        MYLOG.warning(f"Correcting basic channels: {x.shape[1]} to {AUDIO_INFO.SD_CH}")
        if x.shape[1] < channels:
            x = np.column_stack((x, x))
        elif x.shape[1] > channels:
            x = x[:, :1]
    return x


def get_conversion_factor(type_src: str, type_dst: str) -> float | int:
    """ returns conversion factor when changing dtype in numpy array with sound """
    src_float = np.issubdtype(type_src, np.floating)
    dst_float = np.issubdtype(type_dst, np.floating)
    if src_float:
        if dst_float:
            return 1
        else:
            return float(np.iinfo(type_dst).max)
    else:
        if dst_float:
            return 1 / float(np.iinfo(type_src).max)
        else:
            return float(np.iinfo(type_dst).max) / float(np.iinfo(type_src).max)


class AudioInfo:
    __instance = None

    def __new__(cls):
        """ creates a singleton object, if it is not created, else returns existing """
        if not cls.__instance:
            cls.__instance = super(AudioInfo, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True

        dic: dict[str, str] = load_ini_section("AUDIO")
        self.SD_NAME: str = dic.get(ConfigName.device_name, "").strip()
        # noinspection PyBroadException
        try:
            self.DEV_IN: dict[str, any] = sd.query_devices(self.SD_NAME, kind='input')
            self.DEV_OUT: dict[str, any] = sd.query_devices(self.SD_NAME, kind='output')
            sd.default.device = self.SD_NAME
            MYLOG.info(f"Found device matching main.ini name: {self.SD_NAME}")
        except Exception:
            MYLOG.error(f"No device matching main.ini name: {self.SD_NAME}, using default basic device instead")
            self.DEV_IN: dict[str, any] = sd.query_devices(None, kind='input')
            self.DEV_OUT: dict[str, any] = sd.query_devices(None, kind='output')

        MYLOG.debug(f"Using IN/OUT devices:\n{self.DEV_IN}\n\n{self.DEV_OUT}\n\n")

        # =======================================
        if self.DEV_IN["max_input_channels"] not in [1, 2]:
            raise RuntimeError(f"ALSA IN device must have 1 or 2 channels, got {self.DEV_IN['max_input_channels']}")
        if self.DEV_OUT["max_output_channels"] not in [1, 2]:
            raise RuntimeError(f"ALSA OUT device must have 1 or 2 channels, got {self.DEV_OUT['max_output_channels']}")
        # make all mono if IN or OUT is mono
        self.SD_CH = min(self.DEV_IN["max_input_channels"], self.DEV_OUT["max_output_channels"])
        sd.default.channels = self.SD_CH, self.SD_CH

        sd.default.samplerate = SD_RATE

        self.SD_TYPE: str = dic.get(ConfigName.device_type, "int16").strip()
        if self.SD_TYPE not in ['int16', 'float32']:
            raise RuntimeError(f"{ConfigName.device_type} in main.ini must be [in16, float32], found: {self.SD_TYPE}")
        sd.default.dtype = self.SD_TYPE

        sd.default.latency = ('low', 'low')

        tmp = dic.get(ConfigName.drum_volume, "1.0")
        self.DRUM_VOLUME: float = 1.0
        # noinspection PyBroadException
        try:
            self.DRUM_VOLUME = float(tmp)
            self.DRUM_VOLUME = min(self.DRUM_VOLUME, 1.0)
            self.DRUM_VOLUME = max(self.DRUM_VOLUME, 0.1)
        except Exception:
            MYLOG.warning(f"Value of drum_volume is incorrect in main.ini file: {tmp}, using value of 1.0")

        self.MAX_SD_TYPE = get_conversion_factor('float32', self.SD_TYPE)

        MYLOG.warning(f"Using IN/OUT channels: {self.SD_CH}, sample rate: {SD_RATE}, data type: {self.SD_TYPE}")
        sd.check_output_settings(channels=self.SD_CH, dtype=self.SD_TYPE, samplerate=SD_RATE)
        sd.check_input_settings(channels=self.SD_CH, dtype=self.SD_TYPE, samplerate=SD_RATE)

    def vol_db(self, arr: np.ndarray) -> int:
        ratio = max(0.0001, np.max(arr, initial=0) / self.MAX_SD_TYPE)
        return round(20 * log10(ratio))


AUDIO_INFO = AudioInfo()
