import random
from enum import IntEnum
from threading import Timer

import numpy as np

from drum._drumloader import DrumLoader
from utils import CONFLDR
from utils import ConfigName, FileFinder, SD_MAX
from utils import SD_RATE, play_sound_buff


class Intensity(IntEnum):
    SILENT = 0
    LVL1 = 1
    LVL2 = 2
    BREAK = 4


class RealDrum(DrumLoader, FileFinder):
    """Drums generated from patterns with random changes"""

    def __init__(self):
        DrumLoader.__init__(self)
        FileFinder.__init__(self, "config/drums", False, "")
        self.__intensity: Intensity = Intensity.LVL2
        self.__is_break_pending: bool = False
        drum_type: str = CONFLDR.dic.get(ConfigName.drum_type, "")
        tmp = self.first_id(lambda x: self.get_id(x) == drum_type, 0)
        self.go_id(tmp)
        DrumLoader.load(self.get_path())

    @staticmethod
    def change_volume(change_by: int) -> None:
        factor = 1.2 if change_by > 0 else (1 / 1.2)
        v = CONFLDR.dic.get(ConfigName.drum_volume, 1.0) * factor
        if v * DrumLoader.max_volume >= SD_MAX:
            return
        if v * DrumLoader.max_volume < 0.01 * SD_MAX:
            return
        v = round(v, 2)
        CONFLDR.set(ConfigName.drum_volume, v)

        DrumLoader.prepare_all(RDRUM.get_length())

    @staticmethod
    def change_swing(change_by: int) -> None:
        v = CONFLDR.dic.get(ConfigName.drum_swing, 0.5)
        v += (0.25 / 4) if change_by >= 0 else (-0.25 / 4)
        v = min(v, 0.75)
        v = max(v, 0.5)
        CONFLDR.set(ConfigName.drum_swing, v)

        DrumLoader.prepare_all(RDRUM.get_length())

    @staticmethod
    def get_volume() -> float:
        return CONFLDR.dic.get(ConfigName.drum_volume, 1.0) * DrumLoader.max_volume / SD_MAX

    @staticmethod
    def get_swing() -> float:
        return CONFLDR.dic.get(ConfigName.drum_swing, 0.5)

    def load_drum_type(self) -> None:
        drum_type = self.get_item()
        DrumLoader.load(self.get_path())
        DrumLoader.prepare_all(RDRUM.get_length())
        CONFLDR.set(ConfigName.drum_type, drum_type)

    @staticmethod
    def prepare_drum(length: int) -> None:
        """ Non blocking drum init in another thread, length is one bar long and holds drum pattern """
        Timer(0.2, DrumLoader.prepare_all, [length]).start()

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        if self.__intensity == Intensity.SILENT or not RDRUM.get_length():
            return

        if self.__intensity & Intensity.LVL1:
            play_sound_buff(DrumLoader.l1, out_data, idx)
        if self.__intensity & Intensity.LVL2:
            play_sound_buff(DrumLoader.l2, out_data, idx)
        if self.__intensity & Intensity.BREAK:
            play_sound_buff(DrumLoader.bk, out_data, idx)

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

        DrumLoader.random_samples()
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
        return f"RDRUM Length:{RDRUM.get_length()} Intensity:{self.__intensity}"


RDRUM = RealDrum()

if __name__ == "__main__":
    pass
