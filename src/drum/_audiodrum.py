import random
from enum import IntEnum
from threading import Timer
from typing import List

import numpy as np

from drum._audiodrumloader import AudioDrumLoader
from utils import SD_MAX
from utils import SD_RATE
from utils.utilalsa import play_sound_buff


class Intensity(IntEnum):
    SILENT = 0
    LVL1 = 1
    LVL2 = 2
    BREAK = 4


class AudioDrum(AudioDrumLoader):
    """Play drums generated from patterns, change patterns and intencity """

    __swing_values: List[float] = [0.5, 0.56, 0.62, 0.69, 0.75]

    def __init__(self):
        AudioDrumLoader.__init__(self)
        self.__intensity: Intensity = Intensity.LVL2
        self.__is_break_pending: bool = False

    def change_volume(self, change_factor: float) -> None:
        v = round(self.volume * change_factor)
        v = min(100, v)
        v = max(1, round(v))
        self.volume = v
        self.prepare_drum(self.get_length())

    def change_swing(self, change_steps: int) -> None:
        indx: int = 0
        if self.swing in self.__swing_values:
            indx = self.__swing_values.index(self.swing)

        indx += change_steps
        indx = indx % len(self.__swing_values)
        self.swing = self.__swing_values[indx]
        self.prepare_drum(self.get_length())

    def get_volume(self) -> float:
        return self.volume * self.max_volume / SD_MAX

    def get_swing(self) -> float:
        return self.swing

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self.__intensity == Intensity.SILENT or not self.get_length():
            return

        if self.__intensity & Intensity.LVL1:
            play_sound_buff(self.l1, out_data, idx)
        if self.__intensity & Intensity.LVL2:
            play_sound_buff(self.l2, out_data, idx)
        if self.__intensity & Intensity.BREAK:
            play_sound_buff(self.bk, out_data, idx)

    def play_break_later(self, part_len: int, idx: int) -> None:
        if self.__is_break_pending:
            return

        bars = 0.5
        samples = self.get_length() * bars
        idx %= part_len
        start_at = (part_len - idx) - samples
        if start_at > 0:
            self.__is_break_pending = True
            Timer(start_at / SD_RATE, self.play_break_now, [bars]).start()

    def play_break_now(self, bars: float = 0) -> None:
        if self.__intensity == Intensity.SILENT:
            self.__intensity = Intensity.LVL1

        def revert():
            self.__intensity &= ~Intensity.BREAK
            self.__is_break_pending = False

        self.random_samples()
        self.__intensity |= Intensity.BREAK
        if bars <= 0:
            bars = 0.5 if random.random() < 0.5 else 1
        samples = self.get_length() * bars
        Timer(samples / SD_RATE, revert).start()

    def change_intensity(self, change_by: int) -> None:
        i = self.__intensity + change_by
        if i > 3:
            i = 0
        if i < 0:
            i = 3
        self.__intensity = i

    def __str__(self):
        return f"{self._file_finder.get_fixed()} {self._bpm:.2F}"


if __name__ == "__main__":
    pass
