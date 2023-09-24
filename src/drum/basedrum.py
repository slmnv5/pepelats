import random
from abc import abstractmethod, ABC

from utils.utilconfig import SD_RATE
from utils.utillog import get_my_log
from utils.utilother import lst_for_slice

my_log = get_my_log(__name__)


class BaseDrum(ABC):
    def __init__(self):
        self._bar_len: int = 0
        self._bpm: float = 0
        self._ptn_idx: int = 0  # pattern/sound index
        self._ptn_lst: list[any] = list()  # play patterns
        self._drum_level = 0  # intensity of drum

    def _get_drum_levels(self) -> int:
        ptn_len = len(self._ptn_lst)
        if ptn_len < 6:
            return 1
        elif ptn_len < 13:
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
        my_log.info(f"Created drum of type: {self}")

    @abstractmethod
    def play_drums(self, out_data, idx) -> None:
        pass

    @abstractmethod
    def stop_drum(self) -> None:
        pass

    @abstractmethod
    def start_drum(self) -> None:
        pass

    @abstractmethod
    def random_drum(self) -> None:
        lst = lst_for_slice(self._drum_level, len(self._ptn_lst), self._get_drum_levels())
        self._ptn_idx = random.choice(lst)
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
    def set_volume(self, volume: float) -> None:
        pass

    @abstractmethod
    def set_par(self, par: float) -> None:
        """May be swing or smth else"""
        pass

    @abstractmethod
    def get_volume(self) -> float:
        return 1.0

    @abstractmethod
    def get_par(self) -> float:
        """May be swing or smth else"""
        return 1.0

    @abstractmethod
    def show_drum(self) -> str:
        return f"{self}:bpm:{self._bpm:.2F}:vol:{self.get_volume():.2F}"

    @abstractmethod
    def load_drum_config(self, config: str = None, bar_len: int = None) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__[0]}:{self._ptn_idx}/{len(self._ptn_lst)}"
