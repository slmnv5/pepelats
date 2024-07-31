from random import random, choices
from threading import Timer

import numpy as np

from basic.audioinfo import AudioInfo
from drum.basedrum import BaseDrum
from song.songpart import SongPart


class LoopDrum(BaseDrum):
    """ Drum using song part as it's base.
    The song part will record real drum sounds and play along with other parts.
    The last loops is used only for drum fills.
    Other loops selected randomly.
    How often loops are randomized is proportional to self._par.
    """

    def __init__(self, song_part: SongPart):
        BaseDrum.__init__(self)
        self._song_part: SongPart = song_part
        self._par = 0.2  # for this drum - probability to randomize at bar start

    def randomize(self) -> None:
        """ Randomly modify drum by excluding some sounds """
        part = self._song_part
        m: int = part.item_count()
        exclude_lst = choices(range(m), k=(m // 3))
        for k in range(m):
            part.select_idx(k).set_silent(k in exclude_lst or k == m - 1)
        self.start()

    def play_fill(self, idx: int) -> None:
        if not self._bar_len:
            return
        part = self._song_part
        part.select_idx(-1).set_silent(False)
        tmp: int = self._bar_len - (idx % self._bar_len)  # samples to end of bar
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal drums
        Timer(tmp / AudioInfo().SD_RATE, self.randomize).start()

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped:
            return
        if idx % self._bar_len == 0 and random() < self._par:
            self.randomize()
        self._song_part.play(out_data, idx)
