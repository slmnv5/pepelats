from random import random
from threading import Timer

import numpy as np

from buffer.wrapbuffer import WrapBuffer
from drum.basedrum import BaseDrum
from song.songpart import SongPart
from utils.utilaudio import SD_RATE


class LoopDrum(BaseDrum):
    """ Drum using song part as it's base.
    The song part will record real drum sounds and play along with other parts.
    Loop #0 always plays, other loops may be added randomly if drum level > 0
    Random shift is applied to drum loops """

    def __init__(self):
        BaseDrum.__init__(self)
        self.DRUM_SKIP_PROB: float = 0.3
        self.__drum_skip_lst: list[int] = list()
        self._part: SongPart | None = None

    def set_songpart(self, part: SongPart) -> None:
        self._part = part

    def is_playable(self, buff: WrapBuffer) -> bool:
        return id(self._part) != id(buff)

    def get_config(self) -> str:
        return ""

    def randomize(self) -> None:
        self.__drum_skip_lst.clear()
        if not self._part:
            return
        self._part.loops.apply_to_each(lambda x:
                                       self.__drum_skip_lst.append(id(x)) if random() < self.DRUM_SKIP_PROB else 0)

    def play_fill(self, idx: int) -> None:
        self.__drum_skip_lst.clear()
        tmp: int = idx % self._bar_len
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal level
        Timer(tmp / SD_RATE, self.randomize).start()

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped or not self._bar_len or not self._part:
            return
        if idx % self._bar_len == 0:
            if random() < self._par:
                self.randomize()
        loops = self._part.loops
        loops.apply_to_each(lambda x:
                            WrapBuffer.play_samples(x, out_data, idx) if id(x) not in self.__drum_skip_lst else None)

    def iterate_config(self, steps: int) -> None:
        pass

    def show_config(self) -> str:
        return ""

    def show_param(self) -> str:
        return super().show_param()
