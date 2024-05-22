from abc import abstractmethod, ABC
from math import ceil, floor
from random import choice, randrange
from threading import Timer

import numpy as np

from buffer.wrapbuffer import WrapBuffer
from utils.utilconfig import SD_RATE
from utils.utillog import get_my_log

my_log = get_my_log(__name__)


class BaseDrum(ABC):
    # patterns sorted by energy. Low enrgy patterns used for rythm, high enegry for drum fills/breaks
    QUIET_PTRN_FRACTION: float = 0.7
    # Fill/break can not be too short, if short is extended by half a bar
    SMALLEST_FILL_FRACTION: float = 0.1
    # Used to skip some drum sounds for the whole bar
    DRUM_COUNT_LIST: list[int] = [5, 5, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2]

    def __init__(self):
        self._play_drum_count: int = 5
        self._is_stopped: bool = True
        self._bar_len: int = 0
        self._bpm: float = 0
        self._ptn_idx: int = 0  # pattern/sound index
        self._ptn_lst: list[list[np.ndarray]] = list()  # play patterns
        self._is_fill: bool = False  # is playing fill/break
        self._par: float = 0.5  # from 0 to 1,  swing, used by some drum types
        self._volume: float = 0.5  # from 0 to 1

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

    def set_config(self, config: str = None) -> None:
        pass

    def set_bar_len(self, bar_len: int) -> None:
        assert bar_len > 0
        self.stop()
        self._bar_len = bar_len
        self._bpm = 60 * 4 / (bar_len / SD_RATE)
        my_log.info(f"Set bar len for: {self}")

    # noinspection PyUnusedLocal
    # noinspection PyMethodMayBeStatic
    def is_playable(self, buff: WrapBuffer) -> bool:
        """ drum and loop may be the same, avoid double play """
        return True

    @abstractmethod
    def play(self, out_data: np.ndarray, idx: int) -> None:
        pass

    def stop(self) -> None:
        self._is_stopped, self._ptn_idx, self._is_fill = True, 0, False

    def start(self) -> None:
        self._is_stopped = False

    def randomize(self) -> None:
        self._is_fill = False
        self._play_drum_count = choice(self.DRUM_COUNT_LIST)
        lst_len: int = len(self._ptn_lst)
        assert lst_len > 0
        lst_split: int = ceil(lst_len * self.QUIET_PTRN_FRACTION)
        self._ptn_idx = randrange(0, lst_split)
        self.start()

    def play_fill(self, idx: int) -> None:
        if self._is_fill or not self._bar_len:
            return
        self._is_fill = True
        self._play_drum_count = 5
        lst_len: int = len(self._ptn_lst)
        lst_split: int = floor(lst_len * self.QUIET_PTRN_FRACTION)
        self._ptn_idx = randrange(lst_split, lst_len)

        tmp: int = idx % self._bar_len
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal level
        Timer(tmp / SD_RATE, self.randomize).start()

    @abstractmethod
    def show_config(self) -> str:
        return ""

    @abstractmethod
    def iterate_config(self, steps: int) -> None:
        pass

    def __str__(self) -> str:
        cls_name = self.__class__.__name__[0]
        return f"{cls_name}:{self._bpm:.2F}"

    @abstractmethod
    def show_param(self) -> str:
        return f"vol:{self._volume:.2F} par:{self._par:.2F}"

    def get_header(self) -> str:
        return str(self)
