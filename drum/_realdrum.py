import random
from enum import IntEnum
from threading import Timer

import numpy as np

from drum._drumloader import DrumLoader
from utils import SD_MAX
from utils import SD_RATE, play_sound_buff


class Intensity(IntEnum):
    SILENT = 0
    LVL1 = 1
    LVL2 = 2
    BREAK = 4


class RealDrum(DrumLoader):
    """Drums generated from patterns with random changes"""

    def __init__(self):
        DrumLoader.__init__(self)
        self.__intensity: Intensity = Intensity.LVL2
        self.__is_break_pending: bool = False
        self.load()

    def change_volume(self, change_by: int) -> None:
        factor = 1.2 if change_by > 0 else (1 / 1.2)
        v = round(self.volume * factor)
        v = min(100, v)
        v = max(1, round(v))
        self.volume = v
        self.prepare_drum(self.get_length())

    def change_swing(self, change_by: int) -> None:
        v = self.swing
        v += (0.25 / 4) if change_by >= 0 else (-0.25 / 4)
        v = min(v, 0.75)
        v = max(v, 0.5)
        self.swing = v
        self.prepare_drum(RDRUM.get_length())

    def get_volume(self) -> float:
        return self.volume * self.max_volume / SD_MAX

    def get_swing(self) -> float:
        return self.swing

    def load_drum_type(self) -> None:
        self.set_fixed(self.get_item())
        self.load()
        if self.get_length():
            self.prepare_drum(self.get_length())

    def prepare_drum_async(self, length: int) -> None:
        """ Non blocking drum init in another thread, length is one bar long and holds drum pattern """
        Timer(0.2, self.prepare_drum, [length]).start()

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        if self.__intensity == Intensity.SILENT or not RDRUM.get_length():
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
        samples = RDRUM.get_length() * bars
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
        samples = RDRUM.get_length() * bars
        Timer(samples / SD_RATE, revert).start()

    def change_intensity(self, change_by: int) -> None:
        i = self.__intensity + change_by
        if i > 3:
            i = 0
        if i < 0:
            i = 3
        self.__intensity = i

    def __str__(self):
        return f"RealDrum Length:{RDRUM.get_length()} Intensity:{self.__intensity}"


RDRUM = RealDrum()

if __name__ == "__main__":
    pass
