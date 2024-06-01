from abc import abstractmethod, ABC

import numpy as np

from utils.utilconfig import SD_RATE
from utils.utillog import MYLOG


class BaseDrum(ABC):
    # when plpaying drum fill it may not be too short and is extended
    SMALLEST_FILL_FRACTION: float = 0.1

    def __init__(self):
        self._is_stopped: bool = True
        self._bar_len: int = 0
        self._bpm: float = 0
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

    def set_bar_len(self, bar_len: int) -> None:
        self.stop()
        self._bar_len = bar_len
        self._bpm = 0 if not bar_len else 60 * 4 / (bar_len / SD_RATE)
        MYLOG.info(f"Set bar len {self._bar_len} for drum: {self}")

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
    def show_param(self) -> str:
        return f"vol:{self._volume:.2F} par:{self._par:.2F}"

    def get_config(self, get_all: bool = False) -> str:
        return ""

    def set_config(self, config: str = None) -> None:
        pass

    def iterate_config(self, steps: int) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.get_class_name()}:{self._bpm:.2F}"


class FakeDrum(BaseDrum):

    def play(self, out_data: np.ndarray, idx: int) -> None:
        pass

    def randomize(self) -> None:
        pass

    def play_fill(self, idx: int) -> None:
        pass

    def show_param(self) -> str:
        return ""

    def get_bpm(self) -> float:
        return 0.0
