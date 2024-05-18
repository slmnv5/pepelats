from random import random, sample

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
        self._stopped: bool = True
        self._part: SongPart = part

    def play_samples(self, buff: WrapBuffer) -> bool:
        return id(self._part) != id(buff)

    def get_config(self) -> str:
        return ""

    def set_config(self, config: str) -> None:
        return

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if not self._bar_len or self._stopped:
            return
        if idx % self._bar_len == 0:
            if random() < self._par:
                self.random_drum()
        self._part.play_samples(out_data, idx)

    def random_drum(self) -> None:
        self._stopped = False
        loops = self._part.loops
        lp_count: int = loops.item_count()
        # play 1, 2, 3 random loops
        rand_lst: list[int] = sample(range(lp_count), min(self._drum_level + 1, lp_count))
        rand_lst.append(0)
        for k in range(lp_count):
            lp = loops.item_from_idx(k)
            lp.set_silent(k not in rand_lst)

    def load_drum_config(self, bar_len: int = None) -> None:
        self.stop_drum()
        bar_len = self._bar_len if bar_len is None else bar_len
        self._set_bar_len(bar_len)
        self.start_drum()

    def iterate_drum_config(self, steps: int) -> None:
        pass

    def show_drum_config(self) -> str:
        return ""

    def stop_drum(self) -> None:
        self._stopped = True

    def start_drum(self) -> None:
        self.random_drum()

    def show_drum_param(self) -> str:
        return super().show_drum_param()
