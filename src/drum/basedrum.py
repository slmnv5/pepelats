import random
from abc import ABC
from threading import Timer
from typing import List, Any, Dict

import numpy as np

from drum._utildrum import bpm_from_length, Intensity, load_all_patterns
from utils import SD_RATE
from utils.log import LOGGER
from utils.utilother import FileFinder


# noinspection PyMethodMayBeStatic
class FakeDrum:
    """ Prototype or interface, default implemFentation of somes methods """

    def __init__(self):
        self._file_finder = FileFinder("config/drum", False, "")
        self._length: int = 0
        self._bpm: float = 0

    def clear_drum(self) -> None:
        self._length = 0
        self._bpm = 0

    def get_item(self) -> str:
        return self._file_finder.get_item()

    def set_fixed(self, fixed: str) -> None:
        return self._file_finder.set_fixed(fixed)

    def get_str(self) -> str:
        return self._file_finder.get_str()

    def iterate(self, go_fwd: bool) -> None:
        return self._file_finder.iterate(go_fwd)

    def get_length(self) -> int:
        return self._length

    def prepare_drum(self, length: int) -> None:
        pass

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        pass


class RealDrum(FakeDrum, ABC):
    """ load drum patterns, drum sounds, genrate audio bufferes with
    drum tracks using volume and swing parameters """

    def __init__(self):
        super().__init__()
        self._intensity: Intensity = Intensity.LVL1
        self._is_break_pending: bool = False
        self._sounds: Dict = dict()
        self._volume: float = 1.0  # from 0 to 1
        self._max_volume: float = 1.0  # from 0 to 1
        self._swing: float = 0.75
        self._shift: int = 0  # samples shift, play early, fix OS delay

        self._ptn_l1: List[Dict[str, Any]] = []
        self._ptn_l2: List[Dict[str, Any]] = []
        self._ptn_bk: List[Dict[str, Any]] = []
        self._l1 = self._l2 = self._bk = []
        self._snd_l1 = []
        self._snd_l2 = []
        self._snd_bk = []

    def load_drum_type(self) -> None:
        self._file_finder.set_fixed(self._file_finder.get_item())
        self._load_all()
        if self._length:
            self.prepare_drum(self._length)

    def _prepare_all(self, length: int) -> None:
        self._length = 0  # keep it zero until sound load is done
        self._bpm = bpm_from_length(length)
        self._snd_l1 = [self._prepare_one(p, length) for p in self._ptn_l1]
        self._snd_l2 = [self._prepare_one(p, length) for p in self._ptn_l2]
        self._snd_bk = [self._prepare_one(p, length) for p in self._ptn_bk]
        self._l1 = self._l2 = self._bk = self._snd_l1[0]
        self._length = length

    def _prepare_one(self, pattern, length: int) -> Any:
        pass

    def _load_all(self) -> None:
        directory: str = self._file_finder.get_full_name()
        lst1 = ["drum_level1", "drum_level2", "drum_break"]
        lst2 = [self._ptn_l1, self._ptn_l2, self._ptn_bk]
        for k in range(3):
            LOGGER.info(f"Loaded patterns from directory: {directory}, file: {lst1[k]}")
            load_all_patterns(directory, lst1[k], lst2[k], [*self._sounds])

    def change_volume(self, change_factor: float) -> None:
        self._volume = round(self._volume * change_factor, 2)
        self._volume = min(1.0, self._volume)
        self._volume = max(0.03, self._volume)
        self.prepare_drum(self._length)

    def change_swing(self, change_by: float) -> None:
        self._swing += change_by
        if self._swing > 0.75:
            self._swing = 0.5
        elif self._swing < 0.5:
            self._swing = 0.75
        self.prepare_drum(self._length)

    def change_shift(self, change_by: float) -> None:
        self._shift += int(change_by * SD_RATE)
        if self._shift > 0.5 * SD_RATE:
            self._shift = 0
        elif self._shift < 0:
            self._shift = int(0.5 * SD_RATE)
        self.prepare_drum(self._length)

    def show_drum_param(self) -> str:
        return f"Drum parameters:\nvolume(0.0-1.0):{self._volume:.2F}\n" \
               f"swing(0.5-0.75):{self._swing:.2F}\n" \
               f"shift(0.0-0.5):{self._shift / SD_RATE:.2F}"

    def change_intensity(self, change_by: int) -> None:
        i = self._intensity + change_by
        if i > 3:
            i = 0
        if i < 0:
            i = 3
        self._intensity = i

    def play_break_later(self, part_len: int, idx: int) -> None:
        if self._is_break_pending:
            return
        bars = 0.5
        samples = self._length * bars
        idx %= part_len
        start_at = (part_len - idx) - samples
        if start_at > 0:
            self._is_break_pending = True
            Timer(start_at / SD_RATE, self.play_break_now, [bars]).start()

    def play_break_now(self, bars: float = 0) -> None:
        if self._intensity == Intensity.SILENT:
            self._intensity = Intensity.LVL1

        def revert():
            self._intensity &= ~Intensity.BREAK
            self._is_break_pending = False

        self._l2 = random.choice(self._snd_l2)
        self._l1 = random.choice(self._snd_l1)
        self._bk = random.choice(self._snd_bk)
        self._intensity |= Intensity.BREAK
        if bars <= 0:
            bars = 0.5 if random.random() < 0.5 else 1
        samples = self._length * bars
        Timer(samples / SD_RATE, revert).start()

    def __str__(self):
        return f"{self.__class__.__name__} " \
               f"patterns: {len(self._ptn_l1)}/{len(self._ptn_l2)}/{len(self._ptn_bk)}" \
               f", sounds: {len(self._snd_l1)}/{len(self._snd_l2)}/{len(self._snd_bk)}"


if __name__ == "__main__":
    pass
