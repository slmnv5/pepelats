from math import log10

import numpy as np
import sounddevice as sd

from utils.util_config import load_ini_section
from utils.util_log import MY_LOG, ConfigError
from utils.util_name import AppName


def make_buffer(sz: int) -> np.ndarray:
    return np.zeros((sz, AUDIO_INFO.SD_CH), AUDIO_INFO.SD_TYPE)


def correct_sound(x: np.ndarray, channels: int, data_type: str) -> np.ndarray:
    """ Convert numpy array to given channels and datatype """
    assert x.ndim in [1, 2]
    assert channels in [1, 2]
    if x.ndim == 1:
        MY_LOG.error(f"Re-shaping one dimensional array, shape: {x.shape}")
        x = x.reshape(-1, 1)
    if x.dtype != AUDIO_INFO.SD_TYPE:
        MY_LOG.warning(f"Correcting array type: {x.dtype} to {AUDIO_INFO.SD_TYPE}")
        factor = get_dtype_max(data_type) / get_dtype_max(x.dtype)
        x = (x * factor).astype(data_type)

    if x.shape[1] != AUDIO_INFO.SD_CH:
        MY_LOG.warning(f"Correcting audio channels: {x.shape[1]} to {AUDIO_INFO.SD_CH}")
        if x.shape[1] < channels:
            x = np.column_stack((x, x))
        elif x.shape[1] > channels:
            x = x[:, :1]
    return x


def get_dtype_max(data_type: str) -> float:
    if np.issubdtype(data_type, np.floating):
        return 1.0
    else:
        return float(np.iinfo(data_type).max)


class AudioInfo:
    __instance = None

    def __new__(cls):
        """ creates a singleton object """
        if not cls.__instance:
            cls.__instance = super(AudioInfo, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        dic: dict[str, str | int | float] = load_ini_section("AUDIO", True)
        self.SD_NAME: str = dic.get(AppName.device_name, "").strip()
        # noinspection PyBroadException
        try:
            self.DEV_IN: dict = sd.query_devices(self.SD_NAME, kind='input')
            self.DEV_OUT: dict = sd.query_devices(self.SD_NAME, kind='output')
            sd.default.device = self.SD_NAME
            MY_LOG.info(f"Found device matching main.ini name: {self.SD_NAME}")
        except Exception:
            MY_LOG.error(f"No device matching main.ini name: {self.SD_NAME}, using default device instead")
            self.DEV_IN: dict = sd.query_devices(None, kind='input')
            self.DEV_OUT: dict = sd.query_devices(None, kind='output')

        MY_LOG.debug(f"Using IN/OUT devices:\n{self.DEV_IN}\n\n{self.DEV_OUT}\n\n")

        if self.DEV_IN["max_input_channels"] not in [1, 2]:
            raise ConfigError(f"ALSA IN device must have 1 or 2 channels, got {self.DEV_IN['max_input_channels']}")
        if self.DEV_OUT["max_output_channels"] not in [1, 2]:
            raise ConfigError(f"ALSA OUT device must have 1 or 2 channels, got {self.DEV_OUT['max_output_channels']}")
        # make all mono if IN or OUT is mono
        self.SD_CH = min(self.DEV_IN["max_input_channels"], self.DEV_OUT["max_output_channels"])
        sd.default.channels = self.SD_CH, self.SD_CH

        self.SD_RATE = dic.get(AppName.sample_rate, 44100)

        self.SD_TYPE: str = dic.get(AppName.device_type, "int16")

        sd.default.samplerate = self.SD_RATE
        sd.default.dtype = self.SD_TYPE
        sd.default.latency = ('low', 'low')

        self.DRUM_VOLUME = dic.get(AppName.drum_volume, 1.0)

        self.MAX_SD_TYPE = get_dtype_max(self.SD_TYPE)

        self.MAX_LEN = dic.get(AppName.max_len_seconds, 60)
        self.MAX_LEN *= self.SD_RATE

        # 5k ~ 0.1 second. May be late by this time without waiting for next bar start.
        self.LATE_SAMPLES: int = 5000

        sd.check_output_settings(channels=self.SD_CH, dtype=self.SD_TYPE, samplerate=self.SD_RATE)
        sd.check_input_settings(channels=self.SD_CH, dtype=self.SD_TYPE, samplerate=self.SD_RATE)

    def vol_db(self, arr: np.ndarray) -> int:
        ratio = max(0.0001, np.max(arr, initial=0) / self.MAX_SD_TYPE)
        return round(20 * log10(ratio))

    def get_zero_buffer(self, sz: int) -> np.ndarray:
        if not (0 < sz <= AUDIO_INFO.MAX_LEN):
            raise ValueError(f"AudioInfo: size is incorrect: {sz}")
        return np.zeros((sz, self.SD_CH), self.SD_TYPE)


AUDIO_INFO = AudioInfo()
