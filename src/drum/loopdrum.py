from random import choice

import numpy as np

from buffer.wrapbuffer import WrapBuffer
from drum.basedrum import BaseDrum
from song.songpart import SongPart


class LoopDrum(BaseDrum):
    """ Drum using song part as it's base.
    The song part will record real drum sounds and play along with other parts.
    Loop #0 always plays, other loops may be added randomly if drum level > 0
    Random shift is applied to drum loops """

    def __init__(self, part: SongPart):
        BaseDrum.__init__(self)
        self._part: SongPart = part

    def is_playable(self, buff: WrapBuffer) -> bool:
        return id(self._part) != id(buff)

    def get_config(self) -> str:
        return ""

    def randomize(self) -> None:
        self._is_fill = False
        self._play_drum_count = choice(self.DRUM_COUNT_LIST)
        loops = self._part.loops
        self._ptn_idx = 0
        self._ptn_lst.clear()
        loops.apply_to_each(lambda x: self._ptn_lst.append(x if len(self._ptn_lst) < self._play_drum_count else None))
        self.start()

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped or not self._bar_len:
            return
        for loop in [x for x in self._ptn_lst if x]:
            WrapBuffer.play_samples(loop, out_data, idx)

    def iterate_config(self, steps: int) -> None:
        pass

    def show_config(self) -> str:
        return ""

    def show_param(self) -> str:
        return super().show_param()
