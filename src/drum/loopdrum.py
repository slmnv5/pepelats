from random import choice, random
from threading import Timer

import numpy as np

from buffer.wrapbuffer import WrapBuffer
from drum.basedrum import BaseDrum
from song.songpart import SongPart
from utils.utilconfig import SD_RATE


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
        self.start()

    def play_fill(self, idx: int) -> None:
        if self._is_fill or not self._bar_len:
            return
        self._is_fill = True
        self._play_drum_count = 5
        tmp: int = idx % self._bar_len
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal level
        Timer(tmp / SD_RATE, self.randomize).start()

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped or not self._bar_len:
            return
        if idx % self._bar_len == 0:
            if random() < self._par:
                self.randomize()
        loops = self._part.loops
        loops.apply_to_each(lambda x: WrapBuffer.play_samples(x, out_data, idx) if loops.idx_from_item(
            x) < self._play_drum_count else None)

    def iterate_config(self, steps: int) -> None:
        pass

    def show_config(self) -> str:
        return ""

    def show_param(self) -> str:
        return super().show_param()
