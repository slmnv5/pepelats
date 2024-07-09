from random import random, choices
from threading import Timer

import numpy as np

from drum.basedrum import BaseDrum
from song.songpart import SongPart
from utils.utilconfig import SD_RATE


class LoopDrum(BaseDrum):
    """ Drum using song part as it's base.
    The song part will record real drum sounds and play along with other parts. """

    def __init__(self, song_part: SongPart):
        BaseDrum.__init__(self)
        self._song_part: SongPart = song_part
        self._par = 0.2  # for this drum - probability to randomize at bar start

    def randomize(self) -> None:
        loops = self._song_part.loops
        loop_count = loops.item_count()
        play_count: int = round(self._volume * loop_count)
        play_idx_lst = choices(range(play_count), k=play_count)
        play_idx_lst.append(0)
        loops.apply_to_each(lambda x: x.set_silent(loops.idx_from_item(x) not in play_idx_lst))
        self.start()

    def play_fill(self, idx: int) -> None:
        self._song_part.loops.apply_to_each(lambda x: x.set_silent(False))
        tmp: int = idx % self._bar_len
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal level
        Timer(tmp / SD_RATE, self.randomize).start()

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped:
            return
        if idx % self._bar_len == 0 and random() < self._par:
            self.randomize()
        self._song_part.play(out_data, idx)
