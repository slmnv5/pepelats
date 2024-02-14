import random
from abc import abstractmethod, ABC

import numpy as np

from buffer.wrapbuffer import WrapBuffer
from utils.utilconfig import SD_RATE
from utils.utillog import get_my_log

my_log = get_my_log(__name__)


class BaseDrum(ABC):
    _DRUM_LEVELS: int = 3

    def __init__(self):
        self._bar_len: int = 0
        self._bpm: float = 0
        self._ptn_idx: int = 0  # pattern/sound index
        self._ptn_lst: list[any] = list()  # play patterns
        self._drum_level = 0  # intensity of drum
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

    def get_id(self) -> int:
        return id(self)

    def get_bar_len(self) -> int:
        return self._bar_len

    @abstractmethod
    def get_config(self) -> str:
        return ""

    def _set_bar_len(self, bar_len: int) -> None:
        self._bar_len = bar_len
        self._ptn_idx = 0
        self._drum_level = 0
        self._bpm = 0 if not bar_len else 60 * 4 / (bar_len / SD_RATE)
        my_log.info(f"Set bar len for: {self}")

    # noinspection PyUnusedLocal
    # noinspection PyMethodMayBeStatic
    def play_samples(self, buff: WrapBuffer) -> bool:
        """ drum and loop may be the same, avoid double play """
        return True

    @abstractmethod
    def play_drums(self, out_data, idx) -> None:
        pass

    @abstractmethod
    def stop_drum(self) -> None:
        self._ptn_idx, self._drum_level = 0, 0

    @abstractmethod
    def start_drum(self) -> None:
        pass

    @abstractmethod
    def random_drum(self) -> None:
        lst = range(len(self._ptn_lst))
        lst = np.array_split(lst, self._DRUM_LEVELS)
        lst = [x for x in lst if len(x) > 0]
        self._drum_level = 0 if self._drum_level >= len(lst) else self._drum_level
        lst = lst[self._drum_level].tolist()
        if self._ptn_idx in lst:
            lst.remove(self._ptn_idx)
        if lst:
            self._ptn_idx = random.choice(lst)
        self.start_drum()

    def change_drum_level(self, chg: int) -> None:
        self._drum_level = (self._drum_level + chg) % self._DRUM_LEVELS
        self.random_drum()

    @abstractmethod
    def show_drum_config(self) -> str:
        return ""

    @abstractmethod
    def iterate_drum_config(self, steps: int) -> None:
        pass

    @abstractmethod
    def load_drum_config(self, config: str = None, bar_len: int = None) -> None:
        pass

    def __str__(self) -> str:
        cls_name = self.__class__.__name__[0]
        return f"{cls_name}:{self._bpm:.2F}:{self._drum_level}"

    @abstractmethod
    def show_drum_param(self) -> str:
        return f"vol:{self._volume:.2F} par:{self._par:.2F}"

    def get_drum_header(self) -> str:
        return str(self)
