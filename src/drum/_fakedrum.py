from abc import abstractmethod

import numpy as np

from utils import SD_RATE
from utils.log import LOGGER


def bpm_from_length(length: int) -> float:
    bar_seconds: float = length / SD_RATE
    return 60 / (bar_seconds / 4)


# noinspection PyMethodMayBeStatic
class FakeDrum:
    """ Prototype or interface, default implementation of somes methods """

    def __init__(self):
        self._length: int = 0
        self._bpm: float = 0
        self._file_finder = None

    def get_item(self) -> str:
        return self._file_finder.get_item()

    def set_fixed(self, fixed: str) -> None:
        return self._file_finder.set_fixed(fixed)

    def get_str(self) -> str:
        return self._file_finder.get_str()

    def iterate(self, go_fwd: bool) -> None:
        return self._file_finder.iterate(go_fwd)

    def prepare_drum(self, length: int) -> None:
        assert length > 0
        self._length = length
        self._bpm = bpm_from_length(length)
        LOGGER.info(f"Prepared: {self}")

    def clear_drum(self) -> None:
        self._length = 0
        self._bpm = 0
        LOGGER.info(f"Cleared: {self}")

    def get_length(self) -> int:
        return self._length

    @abstractmethod
    def load_drum_type(self) -> None:
        pass

    # ================

    def change_volume(self, change_factor: float) -> None:
        pass

    def change_swing(self, change_steps: int) -> None:
        pass

    def get_volume(self) -> float:
        return 0

    def get_swing(self) -> float:
        return 0

    @abstractmethod
    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        pass

    def play_break_later(self, part_len: int, idx: int) -> None:
        pass

    def play_break_now(self, bars: float = 0) -> None:
        pass

    def change_intensity(self, change_by: int) -> None:
        pass
