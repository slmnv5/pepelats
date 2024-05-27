from abc import abstractmethod, ABC

import numpy as np

from buffer.wrapbuffer import WrapBuffer
from utils.utilconfig import SD_RATE
from utils.utillog import MYLOG


class BaseDrum(ABC):

    def __init__(self):
        self._is_stopped: bool = True
        self._bar_len: int = 0
        self._bpm: float = 0
        self._par: float = 0.5  # from 0 to 1,  swing, used by some drum types
        self._volume: float = 0.5  # from 0 to 1
        # Fill/break can not be too short, if short is extended by half a bar
        self.SMALLEST_FILL_FRACTION: float = 0.1

    def get_pickle_info(self) -> tuple[str, int, float, float]:
        return self.get_config(), self._bar_len, self._volume, self._par

    def set_pickle_info(self, info: tuple[str, int, float, float]) -> None:
        if len(info) != 4:
            MYLOG.error(f"set_picle_info() method incorrect parameter: {info}")
            return
        self.set_config(info[0])
        self.set_bar_len(info[1])
        self.set_volume(info[2])
        self.set_par(info[3])

    def set_volume(self, volume: float) -> None:
        volume = min(1., volume)
        volume = max(0.05, volume)
        self._volume = volume

    def get_volume(self) -> float:
        return self._volume

    def set_par(self, par: float) -> None:
        par = min(1.0, par)
        par = max(0.0, par)
        self._par = par

    def get_par(self) -> float:
        return self._par

    def get_class_name(self) -> str:
        return self.__class__.__name__

    def get_bpm(self) -> float:
        return self._bpm

    def get_bar_len(self) -> int:
        return self._bar_len

    @abstractmethod
    def get_config(self) -> str:
        pass

    @abstractmethod
    def set_config(self, config: str = None) -> None:
        pass

    def set_bar_len(self, bar_len: int) -> None:
        self.stop()
        self._bar_len = bar_len
        self._bpm = 0 if not bar_len else 60 * 4 / (bar_len / SD_RATE)
        MYLOG.info(f"Set bar len for: {self}")

    # noinspection PyUnusedLocal
    # noinspection PyMethodMayBeStatic
    def is_playable(self, buff: WrapBuffer) -> bool:
        """ drum and loop may be the same, avoid double play """
        return True

    @abstractmethod
    def play(self, out_data: np.ndarray, idx: int) -> None:
        pass

    def stop(self) -> None:
        self._is_stopped = True

    def start(self) -> None:
        self._is_stopped = False

    @abstractmethod
    def randomize(self) -> None:
        pass

    @abstractmethod
    def play_fill(self, idx: int) -> None:
        pass

    @abstractmethod
    def show_config(self) -> str:
        return ""

    @abstractmethod
    def iterate_config(self, steps: int) -> None:
        pass

    @abstractmethod
    def show_param(self) -> str:
        return f"vol:{self._volume:.2F} par:{self._par:.2F}"

    def __str__(self) -> str:
        cls_name = self.__class__.__name__[0]
        return f"{cls_name}:{self._bpm:.2F}"
