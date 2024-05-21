import random
from abc import abstractmethod, ABC
from threading import Timer

from buffer.wrapbuffer import WrapBuffer
from utils.utilconfig import SD_RATE
from utils.utillog import get_my_log

my_log = get_my_log(__name__)


class BaseDrum(ABC):

    def __init__(self):
        self._bar_len: int = 0
        self._bpm: float = 0
        self._ptn_idx: int = 0  # pattern/sound index
        self._ptn_lst: list[any] = list()  # play patterns
        self._is_fill: bool = False  # Fill or intense break of rythm
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

    @abstractmethod
    def set_config(self, config: str) -> None:
        pass

    def _set_bar_len(self, bar_len: int) -> None:
        self._bar_len = bar_len
        self._ptn_idx = 0
        self._is_fill = 0
        self._bpm = 0 if not bar_len else 60 * 4 / (bar_len / SD_RATE)
        my_log.info(f"Set bar len for: {self}")

    # noinspection PyUnusedLocal
    # noinspection PyMethodMayBeStatic
    def is_playable(self, buff: WrapBuffer) -> bool:
        """ drum and loop may be the same, avoid double play """
        return True

    @abstractmethod
    def play(self, out_data, idx) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        self._ptn_idx, self._is_fill = 0, 0

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def randomize(self) -> None:
        self._is_fill = False
        lst_len: int = len(self._ptn_lst)
        lst_split: int = round(lst_len * 0.8)
        self._ptn_idx = random.randrange(0, lst_split)
        self.start()

    def play_fill(self, idx: int) -> None:
        if self._is_fill:
            return
        self._is_fill = True
        lst_len: int = len(self._ptn_lst)
        lst_split: int = round(lst_len * 0.8)
        self._ptn_idx = random.randrange(lst_split, lst_len)

        bar_len = self.get_bar_len()
        tmp: int = idx % bar_len
        if tmp < 0.1 * bar_len:
            tmp = tmp + bar_len
        # return to normal level
        Timer(tmp / SD_RATE, self.randomize).start()

    @abstractmethod
    def show_config(self) -> str:
        return ""

    @abstractmethod
    def iterate_config(self, steps: int) -> None:
        pass

    def load_config(self, bar_len: int = None) -> None:
        if not bar_len:
            return
        self.stop()
        self._set_bar_len(bar_len)
        self.start()

    def __str__(self) -> str:
        cls_name = self.__class__.__name__[0]
        return f"{cls_name}:{self._bpm:.2F}"

    @abstractmethod
    def show_param(self) -> str:
        return f"vol:{self._volume:.2F} par:{self._par:.2F}"

    def get_header(self) -> str:
        return str(self)
