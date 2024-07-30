from random import random, choices, randrange
from threading import Timer

import numpy as np

from basic.audioinfo import AudioInfo
from drum.basedrum import BaseDrum
from song.songpart import SongPart


class LoopDrum(BaseDrum):
    """ Drum using song part as it's base.
    The song part will record real drum sounds and play along with other parts.
    First few loops called "quiet" - for normal rhythm, later loops called "loud" - drum fills.
    Loops selected randomly - more self._volume more loops play together.
    How often loops are randomized is proportional to self._par.
    """
    _QUIET_LOOPS = 4

    def __init__(self, song_part: SongPart):
        BaseDrum.__init__(self)
        self._song_part: SongPart = song_part
        self._par = 0.2  # for this drum - probability to randomize at bar start

    def randomize(self) -> None:
        loops = self._song_part.get_list()
        if self._volume < 0.33:
            exclude_cnt = 3
        elif self._volume < 0.66:
            exclude_cnt = 2
        else:
            exclude_cnt = 1

        exclude_lst = choices(range(self._QUIET_LOOPS), k=exclude_cnt)
        for k in range(1, self._QUIET_LOOPS):
            loops[k].set_silent(k in exclude_lst)
        for x in loops[:self._QUIET_LOOPS]:
            x.set_silent(True)

    def play_fill(self, idx: int) -> None:
        loops = self._song_part.get_list()
        try:
            k = randrange(self._QUIET_LOOPS, len(loops))
            loops[k].set_silent(False)  # add one loud loop
        except (ValueError, IndexError):
            for x in loops:
                x.set_silent(False)  # or play all quiet loops

        tmp: int = idx % self._bar_len if self._bar_len else 0
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal level
        Timer(tmp / AudioInfo().SD_RATE, self.randomize).start()

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped:
            return
        if idx % self._bar_len == 0 and random() < self._par:
            self.randomize()
        self._song_part.play(out_data, idx)
