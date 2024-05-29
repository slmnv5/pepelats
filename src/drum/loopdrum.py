from random import random, choices
from threading import Timer

import numpy as np

from drum.basedrum import BaseDrum
from song.songpart import SongPart
from utils.utilconfig import SD_RATE


class LoopDrum(BaseDrum):
    """ Drum using song part as it's base.
    The song part will record real drum sounds and play along with other parts. """

    _COUNT_LST: list[int] = [1, 2, 3, 4, 5]
    _COUNT_WGHT: list[int] = [1, 5, 5, 3, 1]

    def __init__(self):
        BaseDrum.__init__(self)
        self._songpart: SongPart | None = None
        self._par = 0.2  # for this drum - probability to randomize at bar start

    def set_songpart(self, part: SongPart) -> None:
        self._songpart = part

    def start(self) -> None:
        if not self._songpart:
            return
        self._is_stopped = False

    def iterate_config(self, steps: int) -> None:
        pass

    def show_config(self) -> str:
        return ""

    def show_param(self) -> str:
        return super().show_param()

    def get_config(self) -> str:
        return "Loop"

    def set_config(self, config: str = None) -> None:
        pass

    def randomize(self) -> None:
        play_count: int = choices(self._COUNT_LST, weights=self._COUNT_WGHT, k=1)[0]
        loops = self._songpart.loops
        loops.apply_to_each(lambda x: x.set_silent(loops.idx_from_item(x) >= play_count))

    def play_fill(self, idx: int) -> None:
        self._songpart.loops.apply_to_each(lambda x: x.set_silent(False))
        tmp: int = idx % self._bar_len
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal level
        Timer(tmp / SD_RATE, self.randomize).start()

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped or not self._bar_len:
            return
        if idx % self._bar_len == 0 and random() < self._par:
            self.randomize()
        self._songpart.play(out_data, idx)
