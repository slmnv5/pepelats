import random
from abc import abstractmethod, ABC

from utils.utilconfig import SD_RATE
from utils.utillog import get_my_log
from utils.utilother import EuclidSlicer

my_log = get_my_log(__name__)


class BaseDrum(ABC):
    def __init__(self):
        self._bar_len: int = 0
        self._bpm: float = 0
        self._ptn_idx: int = 0  # pattern/sound index
        self._ptn_lst: list[any] = list()  # play patterns
        self._drum_level = 0  # intensity of drum
        self._par: float = 0.6  # from 0 to 1,  swing, used by some drum types
        self._volume: float = 0.7  # from 0 to 1

    def set_volume(self, volume: float) -> None:
        volume = min(1., volume)
        volume = max(0.05, volume)
        if volume != self._volume:
            self._volume = volume

    def get_volume(self) -> float:
        return self._volume

    def set_par(self, par: float) -> None:
        self._par = round(par, 2)
        self._par = min(1.0, self._par)
        self._par = max(0.0, self._par)

    def get_par(self) -> float:
        return self._par

    def _get_drum_levels(self) -> int:
        ptn_len = len(self._ptn_lst)
        if ptn_len < 6:
            return 2
        else:
            return 3

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
        es = EuclidSlicer(len(self._ptn_lst), self._get_drum_levels(), 0)
        sl: slice = es.slice_by_idx(self._drum_level)
        lst = self._ptn_lst[sl]
        self._ptn_idx = sl.start + (random.randrange(len(lst)) if lst else 0)
        self.start_drum()

    @abstractmethod
    def change_drum_level(self, chg: int) -> None:
        self._drum_level = (self._drum_level + chg) % self._get_drum_levels()
        self.random_drum()

    @abstractmethod
    def show_drum_config(self) -> str:
        return ""

    @abstractmethod
    def iterate_drum_config(self, steps: int) -> None:
        pass

    @abstractmethod
    def show_drum(self) -> str:
        return f"{self}:bpm:{self._bpm:.2F}:vol:{self.get_volume():.2F}"

    @abstractmethod
    def load_drum_config(self, config: str = None, bar_len: int = None) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__[0]}:{self._ptn_idx}/{len(self._ptn_lst)}"
