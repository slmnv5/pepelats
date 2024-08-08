from abc import abstractmethod

import numpy as np

from utils.util_audio import AUDIO_INFO
from utils.util_config import load_ini_section
from utils.util_log import MY_LOG
from utils.util_name import AppName


class BaseDrum:

    def __init__(self):
        self._is_stopped: bool = True
        self._bar_len: int = 0
        self._bpm: float = 0
        self._param: float = load_ini_section("DRUM", True).get(AppName.drum_param, 0.5)
        self._volume: float = load_ini_section("DRUM", True).get(AppName.drum_volume, 0.5)

    def set_volume(self, volume: float) -> None:
        volume = min(1., volume)
        volume = max(0.001, volume)
        self._volume = volume

    def get_volume(self) -> float:
        return self._volume

    def set_param(self, par: float) -> None:
        par = min(1.0, par)
        par = max(0.0, par)
        self._param = par

    def get_param(self) -> float:
        return self._param

    def get_class_name(self) -> str:
        return f"{self.__class__.__name__}"

    def get_drum_info(self) -> dict[str, str | float]:
        drum_info: dict[str, str | float] = dict()
        drum_info[AppName.drum_type] = self.get_class_name()
        drum_info[AppName.drum_config_file] = self.get_config()
        drum_info[AppName.drum_volume] = self._volume
        drum_info[AppName.drum_param] = self._param
        drum_info[AppName.drum_len] = self._bar_len
        return drum_info

    def get_bpm(self) -> float:
        return self._bpm

    def get_bar_len(self) -> int:
        return self._bar_len

    def set_bar_len(self, bar_len: int) -> None:
        if bar_len <= 0 or self._bar_len != 0:
            raise RuntimeError("Method set_bar_len must be called only once with positive bar_len")
        self._bar_len = bar_len
        self._bpm = 0 if not bar_len else 60 * 4 / (bar_len / AUDIO_INFO.SD_RATE)
        MY_LOG.info(f"Set bar len {self._bar_len} for drum: {self}")

    def stop(self) -> None:
        self._is_stopped = True

    def start(self) -> None:
        if self._bar_len > 0:
            self._is_stopped = False

    def show_param(self) -> str:
        return f"vol:{self._volume:.2F} par:{self._param:.2F}"

    def get_config(self, include_all: bool = False) -> str:
        return ""

    def set_config(self, config: str = None) -> None:
        pass

    def get_next_config(self) -> str:
        pass

    def get_prev_config(self) -> str:
        pass

    def __str__(self) -> str:
        return f"{self.get_class_name()}:{self._bpm:.2F}"

    @abstractmethod
    def randomize(self) -> None:
        pass

    @abstractmethod
    def play_fill(self) -> None:
        pass

    @abstractmethod
    def play(self, out_data: np.ndarray, idx: int) -> None:
        pass
